"""AutoIntel — Model Lab."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.chart_utils import show_chart
from app.helpers import (
    METRICS_DF,
)


def page_model_comparison() -> None:
    st.markdown("## 🤖 Model Comparison Lab")
    st.markdown(
        '<p style="color:#8892a0">Compare 8 ML models across multiple dimensions</p>',
        unsafe_allow_html=True,
    )

    # Apply explainability mode
    expert = st.session_state.expert_mode

    # Summary table
    display_df = METRICS_DF.copy()
    display_df.index = range(1, len(display_df) + 1)
    if expert:
        display_df["RMSE"] = display_df["RMSE"].apply(lambda x: f"₹{x:,}")
        display_df["MAE"] = display_df["MAE"].apply(lambda x: f"₹{x:,}")
        display_df["Test R²"] = display_df["Test R²"].apply(lambda x: f"{x:.4f}")
        display_df["Time (s)"] = display_df["Time (s)"].apply(lambda x: f"{x:.2f}s")
        st.dataframe(
            display_df[["Model", "Test R²", "RMSE", "MAE", "Time (s)", "Params"]],
            use_container_width=True,
        )
    else:
        st.markdown(
            '<div class="glass-card" style="text-align:center"><strong>🏆 Best Model:</strong> Linear Regression achieves the highest accuracy with R² score of 0.7654, meaning it explains <strong>76.5%</strong> of price variation across cars.</div>',
            unsafe_allow_html=True,
        )

    # Remaining stats shown only in expert mode
    if expert:
        best = METRICS_DF.loc[METRICS_DF["Test R²"].idxmax()]
        st.markdown(
            f'<div class="glass-card" style="text-align:center;border-color:rgba(82,183,136,0.3)">'
            f"🏆 <strong>Best Model:</strong> {best['Model']} — "
            f'R²: <span style="color:#52b788">{best["Test R²"]:.4f}</span> | '
            f'RMSE: <span style="color:#e85d04">₹{best["RMSE"]:,}</span> | '
            f'MAE: <span style="color:#4895ef">₹{best["MAE"]:,}</span></div>',
            unsafe_allow_html=True,
        )

    # R² bar chart (shown in both modes)
    sorted_df = METRICS_DF.sort_values("Test R²")
    colors_r2 = [
        (
            "#52b788"
            if i == len(sorted_df) - 1
            else ("#4895ef" if i > len(sorted_df) - 4 else "#5a6270")
        )
        for i in range(len(sorted_df))
    ]
    fig = go.Figure(
        data=[
            go.Bar(
                x=sorted_df["Test R²"],
                y=sorted_df["Model"],
                orientation="h",
                marker_color=colors_r2,
                text=[f"{v:.4f}" for v in sorted_df["Test R²"]],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(title="R² Score (higher is better)", xaxis_range=[0, 1], height=400)
    show_chart(fig, 400)

    c1, c2 = st.columns(2)
    with c1:
        melted = METRICS_DF.melt(
            id_vars=["Model"],
            value_vars=["RMSE", "MAE"],
            var_name="Metric",
            value_name="Value",
        )
        fig2 = go.Figure()
        for metric, color in [("RMSE", "#e85d04"), ("MAE", "#4895ef")]:
            m = melted[melted["Metric"] == metric]
            fig2.add_trace(go.Bar(name=metric, x=m["Model"], y=m["Value"], marker_color=color))
        fig2.update_layout(
            title="RMSE & MAE (lower is better)",
            barmode="group",
            xaxis_tickangle=-45,
            height=400,
        )
        show_chart(fig2, 400)
    with c2:
        fig3 = go.Figure(
            data=[
                go.Scatter(
                    x=METRICS_DF["Time (s)"],
                    y=METRICS_DF["Test R²"],
                    mode="markers+text",
                    text=METRICS_DF["Model"],
                    textposition="top center",
                    marker={
                        "size": [20 if m == best["Model"] else 12 for m in METRICS_DF["Model"]],
                        "color": [
                            "#e85d04" if m == best["Model"] else "#4895ef"
                            for m in METRICS_DF["Model"]
                        ],
                    },
                )
            ]
        )
        fig3.update_layout(
            title="Training Time vs Performance",
            xaxis_title="Time (s)",
            yaxis_title="R² Score",
            height=400,
        )
        show_chart(fig3, 400)

    # Radar chart
    st.markdown("### 🕸️ Multi-Dimensional Radar")
    radar_models = [
        "Linear Regression",
        "Ridge",
        "XGBoost",
        "Gradient Boosting",
        "SVR",
        "Lasso",
        "KNN",
        "Random Forest",
    ]
    categories = ["R² Score", "Speed", "Accuracy", "Interpretability", "Stability"]
    radar_data = {
        "Linear Regression": [0.9, 0.95, 0.85, 0.95, 0.9],
        "Ridge": [0.88, 0.98, 0.84, 0.9, 0.92],
        "XGBoost": [0.85, 0.7, 0.88, 0.6, 0.8],
        "Gradient Boosting": [0.83, 0.5, 0.85, 0.6, 0.82],
        "SVR": [0.7, 0.2, 0.72, 0.5, 0.65],
        "Lasso": [0.65, 0.9, 0.7, 0.85, 0.78],
        "KNN": [0.62, 0.95, 0.68, 0.5, 0.6],
        "Random Forest": [0.6, 0.6, 0.65, 0.75, 0.7],
    }
    radar_colors = [
        "#e85d04",
        "#4895ef",
        "#52b788",
        "#9b5de5",
        "#f48c06",
        "#00b4d8",
        "#e63946",
        "#6a994e",
    ]
    fig4 = go.Figure()
    for idx, model in enumerate(radar_models):
        vals = radar_data[model] + [radar_data[model][0]]
        fig4.add_trace(
            go.Scatterpolar(
                r=vals,
                theta=[*categories, categories[0]],
                fill="toself",
                name=model,
                line={"color": radar_colors[idx]},
                opacity=0.7,
            )
        )
    fig4.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 1]}},
        title="Model Comparison Radar",
        height=500,
    )
    show_chart(fig4, 500)

    # Hyperparameter tuning results
    st.markdown("### 🔧 Hyperparameter Tuning Results")
    if gs_results:
        tune_tabs = st.tabs([k.replace("_", " ").title() for k in gs_results])
        for i, (name, results) in enumerate(gs_results.items()):
            with tune_tabs[i]:
                params = results.get("params", [])
                scores = results.get("mean_test_score", [])
                if params:
                    gs_df = pd.DataFrame(
                        {
                            "Params": params[:10],
                            "CV R² (log)": [f"{s:.4f}" for s in scores[:10]],
                        }
                    )
                    st.dataframe(gs_df, use_container_width=True)
                if "xgboost" in name:
                    st.markdown(
                        '<div class="glass-card" style="text-align:center;border-left:3px solid #52b788">'
                        '<strong>Improvement Delta:</strong> <span style="color:#52b788">+0.0104 R²</span> '
                        "from tuning XGBoost (0.7359 → 0.7463)</div>",
                        unsafe_allow_html=True,
                    )
                if "gradient_boosting" in name:
                    st.markdown(
                        '<div class="glass-card" style="text-align:center;border-left:3px solid #4895ef">'
                        '<strong>Improvement Delta:</strong> <span style="color:#4895ef">+0.0082 R²</span> '
                        "from tuning Gradient Boosting</div>",
                        unsafe_allow_html=True,
                    )
                if "random_forest" in name:
                    st.markdown(
                        '<div class="glass-card" style="text-align:center;border-left:3px solid #9b5de5">'
                        '<strong>Improvement Delta:</strong> <span style="color:#9b5de5">+0.0035 R²</span> '
                        "from tuning Random Forest</div>",
                        unsafe_allow_html=True,
                    )
    else:
        st.info(
            "GridSearchCV results not available. Run `tune_hyperparameters.py` to generate them."
        )

    # Log Transform impact section (conditional on mode)
    st.markdown("### 📉 Log Transform Impact")
    if expert:
        c1, c2 = st.columns(2)
        with c1:
            fig5 = go.Figure(
                data=[
                    go.Bar(
                        x=["Before Log (R²=0.66)", "After Log (R²=0.77)"],
                        y=[0.66, 0.77],
                        marker_color=["#5a6270", "#52b788"],
                        text=["0.66", "0.77"],
                        textposition="outside",
                    )
                ]
            )
            fig5.update_layout(title="Linear Regression: Before vs After Log Transform", height=300)
            show_chart(fig5, 300)
        with c2:
            fig6 = go.Figure(
                data=[go.Histogram(x=np.log1p(df["Price"]), nbinsx=40, marker_color="#e85d04")]
            )
            fig6.update_layout(
                title="Log-Transformed Price Distribution (skewness: -0.12)", height=300
            )
            show_chart(fig6, 300)
    else:
        st.markdown(
            '<div class="glass-card">📈 <strong>Log Transform Boosted Performance:</strong> By applying a log transformation to car prices, the model accuracy improved from 66% to 77% — the single biggest improvement in this project.</div>',
            unsafe_allow_html=True,
        )

    # Model recommendation engine
    st.markdown("### 🎯 Model Recommendation Engine")
    use_case = st.radio(
        "What matters most?",
        ["Balanced", "Accuracy", "Speed", "Explainability"],
        horizontal=True,
    )
    recs = {
        "Accuracy": (
            "Linear Regression",
            "Best R² score (0.7654) — highly recommended for this dataset",
        ),
        "Speed": ("Ridge", "Fastest training (0.02s) with excellent R² (0.7605)"),
        "Explainability": (
            "Linear Regression",
            "Most interpretable — coefficients show direct price impact per feature",
        ),
        "Balanced": (
            "XGBoost",
            "Great R² (0.7463), fast training, and handles non-linear patterns well",
        ),
    }
    model_name, reason = recs[use_case]
    st.markdown(
        f'<div class="glass-card" style="border-left:4px solid #52b788">'
        f'<strong style="color:#e85d04;font-size:1.1rem">Recommended: {model_name}</strong><br>'
        f'<span style="color:#c8ccd4">{reason}</span></div>',
        unsafe_allow_html=True,
    )
