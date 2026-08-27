"""AutoIntel — Residual Analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app.helpers import (
    FUEL_COLORS,
    METRICS_DF,
    MODEL_METRICS,
    TIER_COLORS,
    compute_deal_score,
    ensemble_prediction,
    fmt_inr,
    generate_data_quality_report,
    generate_natural_language_explanation,
    get_car_name_options,
    get_company_tier,
    get_fuel_simple,
    get_price_tier,
    make_prediction,
    shap_lite_approximation,
)
from app.helpers import get_filtered_data as _get_filtered_data_raw
from app.chart_utils import show_chart


def page_residual_analysis() -> None:
    st.markdown("## 🧪 Residual Analysis")
    st.markdown(
        '<p style="color:#8892a0">Deep-dive into prediction errors for any trained model</p>',
        unsafe_allow_html=True,
    )

    model_names = list(models.keys())
    chosen = st.selectbox("Select Model", model_names, key="ra_model")
    model = models[chosen]

    with st.spinner("Computing residuals..."):
        X_test, _y_test = pp_data["X_test"], pp_data["y_test"]
        y_test_orig = pp_data["y_test_orig"]
        pred_log = model.predict(X_test)
        pred_orig = np.expm1(pred_log)
        residuals = y_test_orig - pred_orig
        pct_errors = np.abs(residuals) / y_test_orig * 100

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            "Mean Residual",
            f"₹{residuals.mean():,.0f}",
            help="Average prediction error",
        )
    with c2:
        st.metric("Std Residual", f"₹{residuals.std():,.0f}")
    with c3:
        st.metric("Avg Error %", f"{pct_errors.mean():.1f}%")

    fig = go.Figure(
        data=[
            go.Scatter(
                x=pred_orig,
                y=residuals,
                mode="markers",
                marker={
                    "color": residuals,
                    "colorscale": "RdYlBu_r",
                    "size": 5,
                    "cmin": -500000,
                    "cmax": 500000,
                    "opacity": 0.5,
                },
                text=[
                    f"Actual: ₹{a:,.0f}<br>Pred: ₹{p:,.0f}<br>Err: {e:.1f}%"
                    for a, p, e in zip(y_test_orig, pred_orig, pct_errors)
                ],
                hovertemplate="%{text}<extra></extra>",
            )
        ]
    )
    fig.add_hline(y=0, line={"color": "#e85d04", "dash": "dash"})
    fig.update_layout(
        title="Residuals vs Predicted",
        xaxis_title="Predicted Price (₹)",
        yaxis_title="Residual (₹)",
        height=400,
    )
    show_chart(fig, 400)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure(data=[go.Histogram(x=residuals, nbinsx=50, marker_color="#4895ef")])
        fig2.add_vline(
            x=residuals.mean(),
            line={"color": "#e85d04", "dash": "dash"},
            annotation_text=f"μ={residuals.mean():,.0f}",
        )
        fig2.add_vline(x=residuals.mean() + residuals.std(), line={"color": "#52b788", "dash": "dot"})
        fig2.add_vline(x=residuals.mean() - residuals.std(), line={"color": "#52b788", "dash": "dot"})
        fig2.update_layout(
            title=f"Residual Distribution (μ±σ: ₹{residuals.std():,.0f})", height=350
        )
        show_chart(fig2, 350)
    with c2:
        sorted_res = np.sort(residuals)
        theoretical = np.random.normal(residuals.mean(), residuals.std(), len(sorted_res))
        theoretical.sort()
        fig3 = go.Figure(
            data=[
                go.Scatter(
                    x=theoretical,
                    y=sorted_res,
                    mode="markers",
                    marker={"color": "#52b788", "size": 4, "opacity": 0.4},
                )
            ]
        )
        min_v = min(theoretical.min(), sorted_res.min())
        max_v = max(theoretical.max(), sorted_res.max())
        fig3.add_trace(
            go.Scatter(
                x=[min_v, max_v],
                y=[min_v, max_v],
                mode="lines",
                line={"color": "#e85d04", "dash": "dash"},
                name="Ideal",
            )
        )
        fig3.update_layout(title="QQ Plot (Normality Check)", height=350)
        show_chart(fig3, 350)

    # Prediction error by company
    st.markdown("### 🏢 Error by Company")
    company_col = pp_data["X_test"][:, 2:38]  # one-hot company columns
    if company_col.shape[1] >= 5:
        company_names = pp_data["feature_names"][2:38]
        company_errors = []
        for idx in range(company_col.shape[1]):
            mask = company_col[:, idx] > 0.5
            if mask.sum() > 5:
                company_errors.append(
                    {
                        "Company": str(company_names[idx]).replace("company_", ""),
                        "Count": int(mask.sum()),
                        "Avg Error ₹": residuals[mask].mean(),
                    }
                )
        if company_errors:
            err_df = pd.DataFrame(company_errors).sort_values("Avg Error ₹", ascending=False)
            fig_err = go.Figure(
                data=[
                    go.Bar(
                        x=err_df["Company"].head(10),
                        y=err_df["Avg Error ₹"].head(10),
                        marker_color=err_df["Avg Error ₹"].head(10),
                        marker_colorscale="RdYlBu_r",
                        text=[fmt_inr(v) for v in err_df["Avg Error ₹"].head(10)],
                    )
                ]
            )
            fig_err.update_layout(
                title="Which Brands Are Hardest to Predict? (Avg Error)",
                xaxis_title="Company",
                yaxis_title="Avg Error (₹)",
                height=350,
                xaxis_tickangle=-45,
            )
            show_chart(fig_err, 350)

    # Calibration curve
    st.markdown("### 📐 Calibration Curve")
    np.sort(y_test_orig)
    percentiles = np.linspace(5, 95, 10, dtype=int)
    actual_cov = []
    predicted_cov = []
    for p in percentiles:
        threshold = np.percentile(pred_orig, p)
        actual_in_range = (y_test_orig <= threshold).mean() * 100
        actual_cov.append(actual_in_range)
        predicted_cov.append(p)
    fig_cal = go.Figure()
    fig_cal.add_trace(
        go.Scatter(
            x=predicted_cov,
            y=actual_cov,
            mode="lines+markers",
            name="Actual Coverage",
            line={"color": "#e85d04", "width": 3},
            marker={"size": 8, "color": "#e85d04"},
        )
    )
    fig_cal.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            name="Ideal",
            line={"color": "#52b788", "dash": "dash"},
        )
    )
    fig_cal.update_layout(
        title="Predicted Confidence vs Actual Coverage",
        xaxis_title="Predicted Percentile",
        yaxis_title="Actual % in Range",
        height=350,
        showlegend=True,
    )
    show_chart(fig_cal, 350)

    # Top 20 worst predictions
    st.markdown("### Top 20 Worst Predictions")
    errors_df = pd.DataFrame({"pred": pred_orig, "actual": y_test_orig, "error_pct": pct_errors})
    worst = errors_df.nlargest(20, "error_pct")
    # Map back to car names if possible
    df.sample(min(len(worst), len(df)))
    worst_display = worst.copy()
    worst_display["Actual"] = worst_display["actual"].apply(fmt_inr)
    worst_display["Predicted"] = worst_display["pred"].apply(fmt_inr)
    worst_display["Error %"] = worst_display["error_pct"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(
        worst_display[["Actual", "Predicted", "Error %"]].head(20),
        use_container_width=True,
    )

    st.markdown("### Prediction Error by Feature")
    c1, c2 = st.columns(2)
    with c1:
        fig4 = go.Figure(
            data=[
                go.Scatter(
                    x=pp_data["X_test"][:, 0],
                    y=residuals,
                    mode="markers",
                    marker={"color": "#9b5de5", "size": 4, "opacity": 0.4},
                )
            ]
        )
        fig4.add_hline(y=0, line={"color": "#e85d04", "dash": "dash"})
        fig4.update_layout(
            title="Error vs Car Age",
            xaxis_title="Car Age (scaled)",
            yaxis_title="Residual (₹)",
            height=300,
        )
        show_chart(fig4, 300)
    with c2:
        fig5 = go.Figure(
            data=[
                go.Scatter(
                    x=pp_data["X_test"][:, 1],
                    y=residuals,
                    mode="markers",
                    marker={"color": "#f48c06", "size": 4, "opacity": 0.4},
                )
            ]
        )
        fig5.add_hline(y=0, line={"color": "#e85d04", "dash": "dash"})
        fig5.update_layout(
            title="Error vs KMs Driven",
            xaxis_title="KMs Driven (scaled)",
            yaxis_title="Residual (₹)",
            height=300,
        )
        show_chart(fig5, 300)
