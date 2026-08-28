"""AutoIntel — Dataset Explorer."""

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


@st.cache_data(ttl=3600)
def get_filtered_data(df, companies, fuels, year_r, price_r, kms_r) -> pd.DataFrame:
    return _get_filtered_data_raw(df, companies, fuels, year_r, price_r, kms_r)
from app.chart_utils import show_chart


def page_dataset_explorer() -> None:
    st.markdown("## 📊 Dataset Explorer")
    st.markdown(
        '<p style="color:#8892a0">Filter, browse, and analyze the car dataset</p>',
        unsafe_allow_html=True,
    )

    # Filters
    with st.expander("🔍 Filters", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            sel_companies = st.multiselect(
                "Company", companies, default=companies[:5], key="de_comp"
            )
        with f2:
            sel_fuels = st.multiselect("Fuel Type", fuel_types, default=fuel_types, key="de_fuel")
        with f3:
            yr_range = st.slider(
                "Year Range",
                int(df["year"].min()),
                int(df["year"].max()),
                (int(df["year"].min()), int(df["year"].max())),
                key="de_yr",
            )
        with f4:
            pr_range = st.slider(
                "Price Range (₹)",
                float(df["Price"].min()),
                float(df["Price"].max()),
                (float(df["Price"].min()), float(df["Price"].max())),
                key="de_pr",
                format="₹%.0f",
            )
        f5, f6 = st.columns(2)
        with f5:
            kms_range = st.slider(
                "KMs Driven",
                0,
                int(df["kms_driven"].max()),
                (0, int(df["kms_driven"].max())),
                key="de_kms",
            )
        with f6:
            if st.button("🎲 Surprise Me", use_container_width=True):
                import random

                sel_companies = [random.choice(companies)]
                sel_fuels = [random.choice(fuel_types)]
                yr = random.randint(2000, 2020)
                yr_range = (yr, yr + 5)
                pr_range = (50000, random.randint(500000, 2000000))
                st.rerun()

    filtered = get_filtered_data(
        df,
        sel_companies if sel_companies else companies,
        sel_fuels if sel_fuels else fuel_types,
        yr_range,
        pr_range,
        kms_range,
    )
    st.markdown(
        f'<p style="color:#c8ccd4">Showing <span style="color:#e85d04;font-weight:700">{len(filtered):,}</span> of {len(df):,} records</p>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📋 Data Table", "📊 Dynamic Charts"])

    with tab1:
        # Color KMs based on condition
        float(df["kms_driven"].median())
        float(df["kms_driven"].quantile(0.75))
        col_config = {
            "name": st.column_config.TextColumn("Car Name", width="large"),
            "company": st.column_config.TextColumn("Company", width="small"),
            "year": st.column_config.NumberColumn("Year", format="%d"),
            "Price": st.column_config.ProgressColumn(
                "Price (₹)",
                format="₹%.0f",
                min_value=0,
                max_value=float(df["Price"].max()),
            ),
            "kms_driven": st.column_config.NumberColumn("KMs Driven", format="%d"),
            "fuel_type": st.column_config.TextColumn("Fuel"),
            "car_age": st.column_config.NumberColumn("Age", format="%d yrs"),
        }
        # Apply conditional coloring on KMs via CSS
        st.markdown(
            """<style>
        .kms-low td:nth-child(5) { color: #52b788 !important; }
        .kms-mid td:nth-child(5) { color: #f48c06 !important; }
        .kms-high td:nth-child(5) { color: #e85d04 !important; }
        </style>""",
            unsafe_allow_html=True,
        )
        st.dataframe(
            filtered.sort_values("Price", ascending=False).reset_index(drop=True),
            column_config=col_config,
            use_container_width=True,
            height=450,
            column_order=[
                "name",
                "company",
                "year",
                "Price",
                "kms_driven",
                "fuel_type",
                "car_age",
            ],
        )

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Filtered CSV",
            csv,
            "filtered_cars.csv",
            "text/csv",
            use_container_width=True,
        )

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(
                data=[
                    go.Histogram(
                        x=filtered["Price"],
                        nbinsx=50,
                        marker_color="#e85d04",
                        opacity=0.8,
                    )
                ]
            )
            fig.update_layout(title="Price Distribution", xaxis_title="Price (₹)")
            show_chart(fig, 300)

            fuel_counts = filtered["fuel_type"].value_counts()
            fig2 = go.Figure(
                data=[
                    go.Pie(
                        labels=fuel_counts.index,
                        values=fuel_counts.values,
                        marker={"colors": [FUEL_COLORS.get(f, "#888") for f in fuel_counts.index]},
                        textinfo="label+percent",
                        hole=0.5,
                    )
                ]
            )
            fig2.update_layout(title="Fuel Breakdown")
            show_chart(fig2, 300)

        with c2:
            fig3 = go.Figure(
                data=[
                    go.Histogram(
                        x=filtered["kms_driven"],
                        nbinsx=50,
                        marker_color="#4895ef",
                        opacity=0.8,
                    )
                ]
            )
            fig3.update_layout(title="KMs Distribution", xaxis_title="Kilometers Driven")
            show_chart(fig3, 300)

            yr_counts = filtered["year"].value_counts().sort_index()
            fig4 = go.Figure(
                data=[go.Bar(x=yr_counts.index, y=yr_counts.values, marker_color="#52b788")]
            )
            fig4.update_layout(title="Year Distribution", xaxis_title="Year", yaxis_title="Count")
            show_chart(fig4, 300)
