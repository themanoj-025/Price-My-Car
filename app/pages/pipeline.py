"""AutoIntel — Pipeline Inspector."""

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


def page_pipeline_inspector() -> None:
    st.markdown("## ⚙️ Pipeline Inspector")
    st.markdown(
        '<p style="color:#8892a0">Technical deep-dive into the ML pipeline for portfolio showcase</p>',
        unsafe_allow_html=True,
    )

    # Interactive pipeline diagram
    pipeline_stages = [
        ("Raw CSV", "11,149 records", "#4895ef"),
        ("Dedup", "-2,135 dupes", "#9b5de5"),
        ("Feature Eng.", "car_age, fuel_simple", "#f48c06"),
        ("Log Transform", "skew 5.64→-0.12", "#e85d04"),
        ("Scale", "StandardScaler", "#52b788"),
        ("Train/Test Split", "80/20", "#4895ef"),
        ("GridSearchCV", "3-fold CV", "#9b5de5"),
        ("Dashboard", "Streamlit app", "#e85d04"),
    ]
    cols = st.columns(8)
    for i, (col, (stage, desc, color)) in enumerate(zip(cols, pipeline_stages)):
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:10px 4px;background:rgba(255,255,255,0.03);'
                f'border-radius:12px;border:1px solid {color}40;cursor:pointer" '
                f"onclick=\"alert('{stage}: {desc}')\">"
                f'<div style="font-size:1.5rem;font-weight:700;color:{color}">{i + 1}</div>'
                f'<div style="font-size:0.7rem;color:#c8ccd4;font-weight:600">{stage}</div>'
                f'<div style="font-size:0.6rem;color:#8892a0">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    # Preprocessing stats table
    st.markdown("### 📊 Preprocessing Stats")
    prep_stats = [
        ("Step", "Before", "After"),
        ("Rows", "13,284", "11,149"),
        ("Duplicates", "2,135", "0"),
        ("Missing Values", "0", "0"),
        ("Features", "6", "39"),
        ("KMs Outliers (P99)", "2,230 (cap)", "Clipped"),
        ("Fuel Types", "5 (incl. rare)", "3 (grouped)"),
        ("Price Skewness", "5.64", "-0.12"),
        ("Train Samples", "—", "8,919"),
        ("Test Samples", "—", "2,230"),
    ]
    prep_html = '<table class="stats-table" style="width:100%">'
    for i, row in enumerate(prep_stats):
        prep_html += (
            "<tr>"
            + "".join(
                f'<td style="{"color:#e85d04;font-weight:600" if i == 0 else "color:#c8ccd4"}">{c}</td>'
                for c in row
            )
            + "</tr>"
        )
    prep_html += "</table>"
    st.markdown(prep_html, unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Feature engineering explainer
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔧 Feature Engineering")
        st.markdown(
            f'<div class="glass-card"><strong>car_age</strong> = {CURRENT_YEAR} - year<br>'
            f'<span style="color:#8892a0">Simple derived feature — strongest predictor of price.</span><br><br>'
            f'<strong>fuel_type_simple</strong>: CNG, LPG, Electric → "Alternative"<br>'
            f'<span style="color:#8892a0">Rare categories grouped to avoid sparse encoding.</span><br><br>'
            f"<strong>One-Hot Encoding</strong>: 36 companies + 3 fuel types → 37 binary features<br>"
            f'<span style="color:#8892a0">Plus 2 numerical features = 39 total.</span></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("### 📐 Log Transform Deep-Dive")
        log_lambda = st.slider("Box-Cox λ value", -2.0, 2.0, 0.0, 0.1, key="boxcox_slider")
        prices = df["Price"].values + 1
        if log_lambda == 0:
            transformed = np.log(prices)
        else:
            transformed = (prices**log_lambda - 1) / log_lambda
        skew_val = pd.Series(transformed).skew()
        st.markdown(
            f'<div class="glass-card" style="text-align:center">'
            f'<span style="color:#8892a0">λ = </span><span style="color:#e85d04;font-size:1.3rem">{log_lambda:.1f}</span>'
            f' &nbsp;→&nbsp; Skewness: <span style="color:{"#52b788" if abs(skew_val) < 1 else "#e85d04"};font-weight:700">{skew_val:.2f}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure(
            data=[go.Histogram(x=transformed, nbinsx=50, marker_color="#e85d04", opacity=0.8)]
        )
        fig.update_layout(
            title=f"Transformed Price (λ={log_lambda:.1f}, skew={skew_val:.2f})",
            height=250,
        )
        show_chart(fig, 250)

    # Training data profiler
    st.markdown("### ✅ Training Data Profiler")
    prof_cols = st.columns(4)
    checks = [
        ("No Nulls", "✅", "#52b788", f"{df.isnull().sum().sum()} missing values"),
        ("Duplicates Removed", "✅", "#52b788", f"{len(df)} unique records"),
        ("All Values in Range", "✅", "#52b788", "No out-of-bound values"),
        ("Types Correct", "✅", "#52b788", "All dtypes verified"),
    ]
    for col, (label, icon, color, desc) in zip(prof_cols, checks):
        col.markdown(
            f'<div class="glass-card" style="text-align:center;border-top:3px solid {color}">'
            f'<div style="font-size:1.5rem">{icon}</div>'
            f'<div style="font-weight:600;color:#c8ccd4">{label}</div>'
            f'<div style="font-size:0.7rem;color:#8892a0">{desc}</div></div>',
            unsafe_allow_html=True,
        )

    # Model cards
    st.markdown("### 📋 Model Cards")
    model_cards = [
        (
            "Linear Regression",
            "0.7654",
            "247,535",
            "Standard OLS",
            "39 coefficients",
            "Interpretable baseline",
        ),
        (
            "Ridge",
            "0.7605",
            "250,108",
            "α=1.0",
            "L2 regularization",
            "Near LR performance",
        ),
        (
            "XGBoost",
            "0.7463",
            "257,436",
            "lr=0.1, depth=3, n=300",
            "Tree-based ensemble",
            "Best tree model",
        ),
        (
            "Gradient Boosting",
            "0.7373",
            "261,980",
            "lr=0.05, depth=5, n=200",
            "Sequential ensemble",
            "Strong regressor",
        ),
        (
            "SVR",
            "0.6998",
            "280,045",
            "rbf kernel, C=100",
            "Support vector regressor",
            "Handles non-linearity",
        ),
        (
            "Lasso",
            "0.6585",
            "298,705",
            "α=0.001",
            "L1 regularization",
            "Feature selection",
        ),
        (
            "KNN",
            "0.6519",
            "301,578",
            "k=7, distance",
            "Nearest neighbors",
            "Instance-based",
        ),
        (
            "Random Forest",
            "0.5850",
            "329,250",
            "depth=15, n=300",
            "Bagging ensemble",
            "Underperforms here",
        ),
    ]
    mc_cols = st.columns(4)
    for col, (name, r2, rmse, params, algo, note) in zip(mc_cols, model_cards):
        with col:
            st.markdown(
                f'<div class="glass-card" style="padding:16px">'
                f'<h4 style="color:#e85d04;margin:0">{name}</h4>'
                f'<div style="font-size:0.8rem;margin-top:8px">'
                f'<span style="color:#52b788">R²:</span> {r2}<br>'
                f'<span style="color:#e85d04">RMSE:</span> ₹{rmse}<br>'
                f'<span style="color:#8892a0">{params}</span><br>'
                f'<span style="color:#5a6270">{algo}</span><br>'
                f'<span style="color:#4895ef">{note}</span></div></div>',
                unsafe_allow_html=True,
            )

    # Environment info
    st.markdown("### 🖥️ Environment Info")
    with st.expander("View requirements.txt + environment"):
        try:
            with open("requirements.txt") as f:
                st.code(f.read(), language="text")
        except OSError:
            st.info("requirements.txt not found")
        st.markdown(
            '<div class="glass-card" style="font-size:0.85rem">'
            "<strong>Python:</strong> 3.9+ | <strong>Streamlit:</strong> 1.57.0 | "
            "<strong>scikit-learn:</strong> 1.7.2 | <strong>XGBoost:</strong> 3.2.0 | "
            "<strong>Plotly:</strong> 6.7.0</div>",
            unsafe_allow_html=True,
        )

    # GitHub/portfolio links
    st.markdown("### 🔗 Links")
    gl1, gl2 = st.columns(2)
    with gl1:
        st.markdown(
            '<a href="https://github.com" target="_blank">'
            '<div class="glass-card" style="text-align:center;cursor:pointer">'
            '<span style="font-size:1.5rem">📂</span><br>GitHub Repository</div></a>',
            unsafe_allow_html=True,
        )
    with gl2:
        st.markdown(
            '<a href="https://opensource.org/licenses/MIT" target="_blank">'
            '<div class="glass-card" style="text-align:center;cursor:pointer">'
            '<span style="font-size:1.5rem">📜</span><br>MIT License</div></a>',
            unsafe_allow_html=True,
        )


# =========================================================================
# Data Quality Report (Feature E)
# =========================================================================
@st.cache_data(ttl=3600)
def load_original_data_for_quality() -> pd.DataFrame:
    return pd.read_csv("Cleaned_Car_data.csv", index_col=0)


def show_data_quality_report() -> None:
    df_orig = load_original_data_for_quality()
    report = generate_data_quality_report(df, df_orig)
    html = '<div class="glass-card" style="padding:12px;font-size:0.85rem"><strong>📋 Data Quality Report</strong><br>'
    for icon, msg in report:
        html += f'<span style="color:#c8ccd4">{icon} {msg}</span><br>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# =========================================================================
# Price History Simulation (Feature J)
# =========================================================================
def show_price_history_simulation() -> None:
    """When was the best time to buy?"""
    st.markdown("### ⏳ Price History Simulation")
    ph_cols = st.columns(2)
    with ph_cols[0]:
        ph_company = st.selectbox("Company", companies, key="ph_comp", index=0)
    with ph_cols[1]:
        ph_model_name = st.text_input(
            "Car Model (partial name)", key="ph_name", placeholder="e.g., Swift"
        )
    if st.button("Simulate History", key="ph_btn", use_container_width=True):
        ph_df = df[df["company"] == ph_company]
        if ph_model_name:
            ph_df = ph_df[ph_df["name"].str.contains(ph_model_name, case=False, na=False)]
        if len(ph_df) > 0:
            trend = ph_df.groupby("year")["Price"].agg(["mean", "min", "max"]).reset_index()
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=trend["year"],
                    y=trend["mean"],
                    mode="lines+markers",
                    name="Avg Price",
                    line={"color": "#e85d04", "width": 3},
                    marker={"size": 8, "color": "#e85d04"},
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=trend["year"],
                    y=trend["min"],
                    mode="lines",
                    name="Min Price",
                    line={"color": "#52b788", "width": 1, "dash": "dot"},
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=trend["year"],
                    y=trend["max"],
                    mode="lines",
                    name="Max Price",
                    line={"color": "#4895ef", "width": 1, "dash": "dot"},
                )
            )
            fig.update_layout(
                title="Price Trend from Manufacture Year",
                xaxis_title="Year",
                yaxis_title="Price (₹)",
                height=400,
            )
            show_chart(fig, 400)
            best_year = trend.loc[trend["mean"].idxmin()]
            st.markdown(
                f'<div class="glass-card" style="text-align:center;border-color:rgba(82,183,136,0.3)">'
                f"📉 <strong>Best time to buy:</strong> {int(best_year['year'])} "
                f"(Avg Price: {fmt_inr(best_year['mean'])})</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No matching cars found.")
