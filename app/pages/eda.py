"""AutoIntel — EDA Deep-Dive."""

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


def page_eda_deepdive() -> None:
    st.markdown("## 🔍 EDA Deep-Dive")
    st.markdown(
        '<p style="color:#8892a0">Comprehensive exploratory data analysis with 5 tabs</p>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        [
            "💰 Price Analysis",
            "🏷️ Brand Intelligence",
            "📊 Feature Correlations",
            "⚠️ Outlier Analysis",
            "📈 Year & Mileage Trends",
        ]
    )

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(
                data=[
                    go.Histogram(
                        x=df["Price"],
                        nbinsx=60,
                        marker_color="#4895ef",
                        opacity=0.8,
                        name="Raw Price",
                    )
                ]
            )
            fig.add_vline(
                x=df["Price"].median(),
                line={"color": "#e85d04", "dash": "dash"},
                annotation_text=f"Median: {fmt_inr(df['Price'].median())}",
            )
            fig.update_layout(
                title=f"Raw Price Distribution (skewness: {df['Price'].skew():.2f})",
                xaxis_title="Price (₹)",
            )
            show_chart(fig, 350)
        with c2:
            log_p = np.log1p(df["Price"])
            fig2 = go.Figure(
                data=[
                    go.Histogram(
                        x=log_p,
                        nbinsx=60,
                        marker_color="#e85d04",
                        opacity=0.8,
                        name="Log Price",
                    )
                ]
            )
            fig2.update_layout(
                title=f"Log-Transformed Price (skewness: {log_p.skew():.2f})",
                xaxis_title="log(Price + 1)",
            )
            show_chart(fig2, 350)

        pct = st.slider("Price Percentile Explorer", 1, 100, 50, 5)
        val = df["Price"].quantile(pct / 100)
        sample = df[df["Price"] >= val].nsmallest(1, "Price")
        st.markdown(
            f'<div class="glass-card" style="text-align:center"><span style="color:#8892a0">P{pct} = </span>'
            f'<span style="color:#e85d04;font-size:1.3rem;font-weight:700">{fmt_inr(val)}</span> — '
            f"Buys a {sample.iloc[0]['name'] if len(sample) > 0 else 'car in this range'} "
            f"({sample.iloc[0]['year'] if len(sample) > 0 else ''})</div>",
            unsafe_allow_html=True,
        )

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            med_prices = df.groupby("company")["Price"].median().sort_values(ascending=True)
            top20 = med_prices.tail(20)
            colors = [
                TIER_COLORS.get(get_company_tier(df[df["company"] == c]["Price"].mean()), "#888")
                for c in top20.index
            ]
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=top20.values,
                        y=top20.index,
                        orientation="h",
                        marker_color=colors,
                        text=[fmt_inr(v) for v in top20.values],
                        textposition="outside",
                    )
                ]
            )
            fig.update_layout(
                title="Top 20 Brands by Median Price",
                xaxis_title="Median Price",
                height=500,
            )
            show_chart(fig, 500)
        with c2:
            brand_stats = (
                df.groupby("company")
                .agg(avg_price=("Price", "mean"), count=("Price", "count"))
                .reset_index()
            )
            brand_stats["tier"] = brand_stats["avg_price"].apply(get_company_tier)
            fig2 = go.Figure(
                data=[
                    go.Scatter(
                        x=brand_stats["count"],
                        y=brand_stats["avg_price"],
                        mode="markers+text",
                        text=brand_stats["company"],
                        textposition="top center",
                        marker={
                            "size": np.sqrt(brand_stats["count"]) * 3,
                            "color": [TIER_COLORS.get(t, "#888") for t in brand_stats["tier"]],
                            "line": {"color": "white", "width": 1},
                        },
                        textfont={"size": 8},
                    )
                ]
            )
            fig2.update_layout(
                title="Brand Positioning: Volume vs Price",
                xaxis_title="Number of Listings",
                yaxis_title="Avg Price (₹)",
                height=500,
            )
            show_chart(fig2, 500)

        st.markdown("### Brand Comparison")
        sel_brands = st.multiselect(
            "Select 2-4 brands to compare",
            companies,
            default=["Maruti", "Hyundai", "BMW", "Mercedes-Benz"],
        )
        if len(sel_brands) >= 2:
            fig3 = go.Figure()
            for brand in sel_brands:
                bdata = df[df["company"] == brand]["Price"] / 1e5
                fig3.add_trace(
                    go.Box(
                        y=bdata,
                        name=brand,
                        marker_color=TIER_COLORS.get(
                            get_company_tier(df[df["company"] == brand]["Price"].mean()),
                            "#888",
                        ),
                        boxmean="sd",
                    )
                )
            fig3.update_layout(
                title="Price Distribution Comparison (in lakhs)",
                yaxis_title="Price (₹ Lakhs)",
                height=400,
            )
            show_chart(fig3, 400)

    with tabs[2]:
        num_cols = ["Price", "year", "kms_driven", "car_age"]
        corr = df[num_cols].corr()
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                text=np.round(corr.values, 3),
                texttemplate="%{text}",
                textfont={"size": 12, "color": "white"},
                colorscale="RdBu_r",
                zmin=-1,
                zmax=1,
            )
        )
        fig.update_layout(title="Correlation Matrix", height=450)
        show_chart(fig, 450)

        # Scatter matrix (using go instead of px)
        sample_df = df.sample(min(2000, len(df)))
        fig2 = make_subplots(
            rows=3,
            cols=3,
            shared_xaxes=True,
            shared_yaxes=True,
            subplot_titles=["Price", "car_age", "kms_driven"],
        )
        dims = ["Price", "car_age", "kms_driven"]
        for i, dim_y in enumerate(dims):
            for j, dim_x in enumerate(dims):
                if i != j:
                    for fuel, color in FUEL_COLORS.items():
                        subset = sample_df[sample_df["fuel_type"] == fuel]
                        fig2.add_trace(
                            go.Scatter(
                                x=subset[dim_x],
                                y=subset[dim_y],
                                mode="markers",
                                marker={"color": color, "size": 3, "opacity": 0.4},
                                name=fuel,
                                showlegend=(i == 0 and j == 1),
                            ),
                            row=i + 1,
                            col=j + 1,
                        )
                else:
                    fig2.add_trace(
                        go.Histogram(x=sample_df[dim_x], marker_color="#4895ef", showlegend=False),
                        row=i + 1,
                        col=j + 1,
                    )
                fig2.update_xaxes(title_text=dim_x if i == 2 else "", row=i + 1, col=j + 1)
                fig2.update_yaxes(title_text=dim_y if j == 0 else "", row=i + 1, col=j + 1)
        fig2.update_layout(title="Scatter Matrix: Price × Car Age × KMs Driven", height=600)
        show_chart(fig2, 600)

        # VIF table for multicollinearity check
        st.markdown("### VIF — Variance Inflation Factor")
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor

            vif_df = df[["Price", "car_age", "kms_driven"]].dropna()
            vif_data = pd.DataFrame()
            vif_data["Feature"] = vif_df.columns
            vif_data["VIF"] = [
                variance_inflation_factor(vif_df.values, i) for i in range(vif_df.shape[1])
            ]
            st.dataframe(
                vif_data.style.applymap(
                    lambda v: (
                        "color:#e85d04"
                        if v > 10
                        else ("color:#f48c06" if v > 5 else "color:#52b788")
                    ),
                    subset=["VIF"],
                ),
                use_container_width=True,
            )
            st.caption("VIF > 10 indicates severe multicollinearity; > 5 moderate; < 5 low.")
        except ImportError:
            # Manual VIF approximation
            corr = df[["Price", "car_age", "kms_driven"]].corr()
            vif_approx = []
            for col in ["Price", "car_age", "kms_driven"]:
                r2_other = 0
                for other in ["Price", "car_age", "kms_driven"]:
                    if other != col:
                        r2_other = max(r2_other, corr.loc[col, other] ** 2)
                vif_approx.append(1 / (1 - r2_other)) if r2_other < 1 else 0
            vif_data = pd.DataFrame(
                {
                    "Feature": ["Price", "car_age", "kms_driven"],
                    "VIF": [f"{v:.2f}" for v in vif_approx],
                }
            )
            st.dataframe(vif_data, use_container_width=True)
            st.caption(
                "VIF estimated via max pairwise R² (install statsmodels for exact calculation)."
            )

    with tabs[3]:
        st.markdown("### IQR-Based Outlier Detection")
        c1, c2 = st.columns(2)
        outliers_info = []
        for col in ["Price", "kms_driven"]:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            n_out = ((df[col] < lower) | (df[col] > upper)).sum()
            outliers_info.append(
                (
                    col,
                    n_out,
                    f"{fmt_inr(lower)} – {fmt_inr(upper)}",
                    f"{fmt_inr(Q1)} – {fmt_inr(Q3)}",
                )
            )
        out_df = pd.DataFrame(
            outliers_info,
            columns=["Feature", "Outliers", "Outlier Bounds", "IQR Range"],
        )
        st.dataframe(out_df, use_container_width=True)

        st.markdown("### Before/After: KMs Driven Capping")
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=df["car_age"],
                        y=df["kms_driven"],
                        mode="markers",
                        marker={"color": "#4895ef", "size": 4, "opacity": 0.4},
                    )
                ]
            )
            fig.update_layout(
                title="Before Capping", xaxis_title="Car Age", yaxis_title="KMs Driven"
            )
            show_chart(fig, 300)
        with c2:
            capped = df["kms_driven"].clip(upper=df["kms_driven"].quantile(0.99))
            fig2 = go.Figure(
                data=[
                    go.Scatter(
                        x=df["car_age"],
                        y=capped,
                        mode="markers",
                        marker={"color": "#52b788", "size": 4, "opacity": 0.4},
                    )
                ]
            )
            fig2.update_layout(
                title="After Capping at P99",
                xaxis_title="Car Age",
                yaxis_title="KMs Driven",
            )
            show_chart(fig2, 300)

        fig3 = go.Figure()
        for col in ["Price", "kms_driven", "car_age"]:
            fig3.add_trace(go.Box(y=df[col], name=col.replace("_", " ").title()))
        fig3.update_layout(title="Box Plots with Outliers Highlighted", height=400)
        show_chart(fig3, 400)

    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            med_by_year = df.groupby("year")["Price"].median().reset_index()
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=med_by_year["year"],
                        y=med_by_year["Price"],
                        mode="lines+markers",
                        line={"color": "#e85d04", "width": 3},
                        marker={"size": 6, "color": "#e85d04"},
                    )
                ]
            )
            fig.update_layout(
                title="Median Price by Year (2000–2024) — Click 'Animate' to play",
                xaxis_title="Year",
                yaxis_title="Median Price (₹)",
                sliders=[
                    {
                        "steps": [
                            {
                                "args": [
                                    [yr],
                                    {"frame": {"duration": 500, "redraw": True}},
                                ],
                                "label": str(yr),
                                "method": "animate",
                            }
                            for yr in med_by_year["year"][::2]
                        ],
                        "active": len(med_by_year) - 1,
                        "currentvalue": {"prefix": "Year: "},
                    }
                ],
                updatemenus=[
                    {
                        "buttons": [
                            {
                                "args": [
                                    None,
                                    {
                                        "frame": {"duration": 300, "redraw": True},
                                        "fromcurrent": True,
                                    },
                                ],
                                "label": "▶ Play",
                                "method": "animate",
                            },
                            {
                                "args": [
                                    [None],
                                    {
                                        "frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate",
                                    },
                                ],
                                "label": "⏹ Pause",
                                "method": "animate",
                            },
                        ],
                        "type": "buttons",
                        "x": 0.5,
                        "y": -0.2,
                        "xanchor": "center",
                    }
                ],
            )
            # Create animation frames
            frames = []
            for yr in med_by_year["year"]:
                trace_data = med_by_year[med_by_year["year"] <= yr]
                frames.append(
                    go.Frame(
                        data=[
                            go.Scatter(
                                x=trace_data["year"],
                                y=trace_data["Price"],
                                mode="lines+markers",
                                marker={"color": "#e85d04"},
                                line={"color": "#e85d04"},
                            )
                        ],
                        name=str(yr),
                    )
                )
            fig.frames = frames
            show_chart(fig, 400)
        with c2:
            sample2 = df.sample(min(2000, len(df)))
            fig2 = go.Figure(
                data=go.Histogram2d(
                    x=sample2["kms_driven"],
                    y=sample2["Price"],
                    colorscale="Hot",
                    nbinsx=30,
                    nbinsy=30,
                )
            )
            fig2.update_layout(
                title="Density: KMs Driven vs Price",
                xaxis_title="KMs Driven",
                yaxis_title="Price (₹)",
            )
            show_chart(fig2, 400)
