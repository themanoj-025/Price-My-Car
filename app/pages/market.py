"""AutoIntel — Market Intelligence."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.chart_utils import show_chart
from app.helpers import (
    TIER_COLORS,
    fmt_inr,
    get_company_tier,
    get_fuel_simple,
    make_prediction,
)


def page_market_intelligence() -> None:
    st.markdown("## 📈 Market Intelligence")
    st.markdown(
        '<p style="color:#8892a0">Price trends, market heatmaps, and value analysis</p>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        # Price trend forecast
        med_by_year = df.groupby("year")["Price"].median().reset_index()
        med_by_year = med_by_year[med_by_year["year"] >= 2000]
        x = med_by_year["year"].values
        y = med_by_year["Price"].values
        if len(x) > 3:
            z = np.polyfit(x, y, 2)
            p = np.poly1d(z)
            future_years = np.array([2025, 2026, 2027])
            future_prices = p(future_years)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers+lines",
                    name="Historical",
                    marker={"color": "#4895ef", "size": 6},
                    line={"color": "#4895ef", "width": 2},
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=future_years,
                    y=future_prices,
                    mode="markers+lines",
                    name="Forecast",
                    marker={"color": "#e85d04", "size": 8, "symbol": "star"},
                    line={"color": "#e85d04", "width": 2, "dash": "dot"},
                )
            )
            fig.update_layout(
                title="Price Trend & Forecast (2025–2027)",
                xaxis_title="Year",
                yaxis_title="Median Price (₹)",
                height=400,
            )
            show_chart(fig, 400)

    with c2:
        # Market heatmap
        heatmap_data = df.pivot_table(
            values="Price", index="company", columns="year", aggfunc="median"
        )
        heatmap_data = heatmap_data.loc[heatmap_data.count(axis=1) > 5, :]
        heatmap_data = heatmap_data.iloc[:15, :]
        fig2 = go.Figure(
            data=go.Heatmap(
                z=np.log1p(heatmap_data.values),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale="Hot",
                text=np.round(heatmap_data.values / 1e5, 1),
                texttemplate="%{text}L",
                textfont={"size": 8},
            )
        )
        fig2.update_layout(title="Brand × Year Price Heatmap (in lakhs)", height=500)
        show_chart(fig2, 500)

    st.markdown("### 💰 Depreciation Calculator")
    dc1, dc2, dc3 = st.columns(3)
    cars_for_dep = []
    for ci, (col, default_comp) in enumerate(zip([dc1, dc2, dc3], ["Maruti", "Hyundai", "BMW"], strict=False)):
        with col:
            dc_comp = st.selectbox(
                f"Car {ci + 1} Brand",
                companies,
                key=f"dc_comp_{ci}",
                index=companies.index(default_comp) if default_comp in companies else 0,
            )
            dc_year = st.slider(f"Car {ci + 1} Year", 2000, 2024, 2018, key=f"dc_year_{ci}")
            dc_kms = st.number_input(
                f"Car {ci + 1} KMs", 0, 200000, 50000, key=f"dc_kms_{ci}", step=10000
            )
            dc_fuel = st.selectbox(f"Car {ci + 1} Fuel", fuel_types, key=f"dc_fuel_{ci}", index=0)
            cars_for_dep.append({"comp": dc_comp, "year": dc_year, "kms": dc_kms, "fuel": dc_fuel})
    if st.button("Compare Depreciation", key="dep_btn", use_container_width=True):
        fig_dep = go.Figure()
        colors_dep = ["#e85d04", "#4895ef", "#52b788"]
        for ci, car in enumerate(cars_for_dep):
            inp_df = pd.DataFrame(
                [
                    {
                        "car_age": CURRENT_YEAR - car["year"],
                        "kms_driven": car["kms"],
                        "company": car["comp"],
                        "fuel_type_simple": get_fuel_simple(car["fuel"]),
                    }
                ]
            )
            if "Linear Regression" in models:
                base_price = make_prediction(models["Linear Regression"], inp_df, preprocessor)
            else:
                base_price = 500000
            years = list(range(11))
            vals = [base_price * (0.88**y) for y in years]
            fig_dep.add_trace(
                go.Scatter(
                    x=[f"Year {y}" if y > 0 else "Now" for y in years],
                    y=vals,
                    mode="lines+markers",
                    name=f"{car['comp']} ({car['year']})",
                    line={"color": colors_dep[ci], "width": 3},
                    marker={"size": 6, "color": colors_dep[ci]},
                )
            )
        fig_dep.update_layout(
            title="10-Year Depreciation Comparison",
            yaxis_title="Estimated Value (₹)",
            height=400,
            showlegend=True,
        )
        show_chart(fig_dep, 400)
    budget = st.slider(
        "Your Budget (₹)",
        100000,
        5000000,
        500000,
        50000,
        format="₹%d",
        key="budget_slider",
    )
    budget_df = df[(df["Price"] >= budget * 0.8) & (df["Price"] <= budget * 1.2)].copy()
    if len(budget_df) > 0:
        budget_df["value_score"] = (
            (1 / (budget_df["car_age"] + 1)) * 0.4
            + (1 / (budget_df["kms_driven"] / 10000 + 1)) * 0.3
            + (budget / budget_df["Price"]).clip(0, 2) * 0.3
        )
        budget_df["value_score"] = budget_df["value_score"] / budget_df["value_score"].max() * 100
        best_values = budget_df.nlargest(5, "value_score")
        st.markdown(f"### Top 5 Best Value Cars Around {fmt_inr(budget)}")
        for _, row in best_values.iterrows():
            st.markdown(
                f'<div class="glass-card" style="padding:12px;display:flex;justify-content:space-between">'
                f"<span><strong>{row['name']}</strong> · {row['company']} · {row['year']}</span>"
                f'<span style="color:#e85d04">{fmt_inr(row["Price"])}</span>'
                f'<span style="color:#52b788">Score: {row["value_score"]:.0f}/100</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No cars found in this budget range.")

    # Brand tier positioning
    st.markdown("### Brand Tier Positioning")
    brand_stats2 = (
        df.groupby("company")
        .agg(avg_price=("Price", "mean"), count=("Price", "count"))
        .reset_index()
    )
    brand_stats2["tier"] = brand_stats2["avg_price"].apply(get_company_tier)
    fig3 = go.Figure()
    for tier, color in TIER_COLORS.items():
        tdata = brand_stats2[brand_stats2["tier"] == tier]
        if len(tdata) > 0:
            fig3.add_trace(
                go.Scatter(
                    x=tdata["count"],
                    y=tdata["avg_price"],
                    mode="markers+text",
                    name=tier,
                    text=tdata["company"],
                    textposition="top center",
                    textfont={"size": 8, "color": color},
                    marker={"size": 12, "color": color, "line": {"color": "white", "width": 1}},
                )
            )
    fig3.update_layout(
        title="Brand Positioning: Price vs Volume",
        xaxis_title="Number of Listings",
        yaxis_title="Avg Price (₹)",
        height=500,
    )
    show_chart(fig3, 500)

    # Price alert simulator
    st.markdown("### 🔔 Price Alert Simulator")
    pa1, pa2, pa3, pa4 = st.columns(4)
    with pa1:
        pa_company = st.selectbox("Company", companies, key="pa_comp", index=0)
    with pa2:
        pa_fuel = st.selectbox("Fuel", fuel_types, key="pa_fuel", index=0)
    with pa3:
        pa_year = st.number_input("Year", 2000, 2024, 2018, key="pa_year")
    with pa4:
        pa_price = st.number_input(
            "Asking Price (₹)", 10000, 5000000, 500000, step=50000, key="pa_price"
        )
    if st.button("Check Deal", key="pa_btn", use_container_width=True):
        inp = pd.DataFrame(
            [
                {
                    "car_age": CURRENT_YEAR - pa_year,
                    "kms_driven": 50000,
                    "company": pa_company,
                    "fuel_type_simple": get_fuel_simple(pa_fuel),
                }
            ]
        )
        if "Linear Regression" in models:
            predicted = make_prediction(models["Linear Regression"], inp, preprocessor)
            deviation = (pa_price - predicted) / predicted * 100
            if abs(deviation) < 5:
                verdict = "✅ Fairly Priced"
                vcolor = "#52b788"
            elif deviation < -5:
                verdict = "🔥 Underpriced — Great Deal!"
                vcolor = "#e85d04"
            else:
                verdict = "⚠️ Overpriced — Consider negotiating"
                vcolor = "#f48c06"
            st.markdown(
                f'<div class="glass-card" style="text-align:center;border-left:4px solid {vcolor}">'
                f'<h3 style="color:{vcolor};margin:0">{verdict}</h3>'
                f'<p style="color:#c8ccd4">Market Value: <strong>{fmt_inr(predicted)}</strong> | '
                f"Asking: <strong>{fmt_inr(pa_price)}</strong> | "
                f'Deviation: <strong style="color:{vcolor}">{deviation:+.1f}%</strong></p></div>',
                unsafe_allow_html=True,
            )
