"""Helper functions for the Price Predictor page.

Extracted from predictor.py for maintainability. Contains bulk prediction
upload processing and model drift simulation logic.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.chart_utils import show_chart
from app.helpers import (
    MODEL_METRICS,
    fmt_inr,
    get_fuel_simple,
    make_prediction,
)

CURRENT_YEAR = 2025


def render_bulk_prediction(models: dict, preprocessor: object) -> None:
    """Render the bulk prediction upload section."""
    st.markdown("### 📦 Bulk Prediction Upload")
    uploaded_file = st.file_uploader(
        "Upload CSV with same schema (name, company, year, kms_driven, fuel_type)",
        type=["csv"],
        key="bulk_upload",
    )
    if uploaded_file:
        try:
            bulk_df = pd.read_csv(uploaded_file)
            required = ["company", "year", "kms_driven", "fuel_type"]
            if all(c in bulk_df.columns for c in required):
                results_list = []
                for _, row in bulk_df.iterrows():
                    inp = pd.DataFrame(
                        [
                            {
                                "car_age": CURRENT_YEAR - row["year"],
                                "kms_driven": row["kms_driven"],
                                "company": row["company"],
                                "fuel_type_simple": get_fuel_simple(row["fuel_type"]),
                            }
                        ]
                    )
                    for m_name in [
                        "Linear Regression",
                        "XGBoost",
                        "Gradient Boosting",
                        "Ridge",
                        "SVR",
                        "Lasso",
                        "KNN",
                        "Random Forest",
                    ]:
                        if m_name in models:
                            p = make_prediction(models[m_name], inp, preprocessor)
                            results_list.append(
                                {
                                    **{c: row[c] for c in required},
                                    "Model": m_name,
                                    "Predicted Price": p,
                                }
                            )
                if results_list:
                    res_df = pd.DataFrame(results_list)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        res_pivot = res_df.pivot_table(
                            index=["company", "year", "kms_driven", "fuel_type"],
                            columns="Model",
                            values="Predicted Price",
                        )
                        res_pivot["Ensemble (Avg)"] = res_pivot.mean(axis=1)
                        res_pivot.to_excel(writer, sheet_name="Predictions")
                        pd.DataFrame(MODEL_METRICS).to_excel(
                            writer, sheet_name="Model Stats", index=False
                        )
                    st.success(
                        f"✅ Processed {len(bulk_df)} records — {len(results_list)} predictions generated!"
                    )
                    st.download_button(
                        "📥 Download Results (Excel)",
                        output.getvalue(),
                        "bulk_predictions.xlsx",
                        use_container_width=True,
                    )
            else:
                st.error(f"CSV must contain columns: {', '.join(required)}")
        except (ValueError, KeyError) as e:
            st.error(f"Error processing file: {e}")


def render_drift_simulator(df: pd.DataFrame) -> None:
    """Render the model drift simulator section."""
    with st.expander("⏱️ Model Drift Simulator — Fast Forward to 2027"):
        drift_year = st.slider("Fast forward to year", 2025, 2030, 2027, key="drift_slider")
        if st.button("Simulate Drift", key="drift_btn"):
            drift_age = drift_year - CURRENT_YEAR
            st.markdown(
                f'<div class="glass-card"><strong>Drift Simulation for {drift_year}</strong><br>'
                f"If car ages increase by {drift_age} years, predictions would shift downward.<br>"
                f'<span style="color:#8892a0">Car age is the strongest predictor — older cars lose value rapidly.</span></div>',
                unsafe_allow_html=True,
            )
            fig = go.Figure()
            fig.add_trace(
                go.Histogram(
                    x=df["Price"],
                    nbinsx=50,
                    name="Current",
                    opacity=0.6,
                    marker_color="#4895ef",
                )
            )
            drift_prices = df["Price"] * (0.92**drift_age)
            fig.add_trace(
                go.Histogram(
                    x=drift_prices,
                    nbinsx=50,
                    name=f"{drift_year} Projection",
                    opacity=0.6,
                    marker_color="#e85d04",
                )
            )
            fig.update_layout(
                title=f"Price Distribution Shift: Current vs {drift_year}",
                barmode="overlay",
                height=350,
            )
            show_chart(fig, 350)
