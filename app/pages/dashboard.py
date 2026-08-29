"""AutoIntel — Dashboard Home."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.helpers import (
    fmt_inr,
    get_fuel_simple,
    get_price_tier,
    make_prediction,
)


def page_dashboard_home() -> None:
    st.markdown(
        '<p class="hero-text">AutoIntel — Used Car Price Intelligence</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#8892a0;font-size:1.1rem;margin-top:-8px">'
        "AI-powered insights into the Indian used car market — 11,149 listings analyzed with 8 ML models</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # KPI metric cards with animated counters (JS via st.components.v1.html)
    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_data = [
        ("Total Records", f"{len(df):,}", "Raw dataset size"),
        ("Cleaned Records", "11,149", "After dedup & cleaning"),
        ("Best R² Score", "0.7654", "+0.01", "Linear Regression"),
        ("Price Range", "₹20K – ₹1Cr", "Min to max"),
        ("Features Eng.", "39", "After encoding & scaling"),
    ]
    for col, kpi in zip([k1, k2, k3, k4, k5], kpi_data):
        if len(kpi) == 4:
            label, val, delta, help_text = kpi
            col.metric(label, val, delta=delta, help=help_text)
        else:
            label, val, help_text = kpi
            col.metric(label, val, help=help_text)

    # Animated counter JS for KPI metrics
    kpi_html = "<script>"
    kpi_html += 'document.querySelectorAll("[data-testid=stMetricValue]").forEach(el => {'
    kpi_html += '  const target = el.textContent.replace(/[^0-9.,KLCr]/g, "").trim();'
    kpi_html += "  if (!target) return;"
    kpi_html += '  const numeric = parseFloat(target.replace(/,/g, "")) || 0;'
    kpi_html += '  const suffix = target.replace(/[0-9.,]/g, "").trim();'
    kpi_html += "  let current = 0;"
    kpi_html += "  const step = Math.max(1, Math.floor(numeric / 40));"
    kpi_html += "  const interval = setInterval(() => {"
    kpi_html += "    current += step;"
    kpi_html += "    if (current >= numeric) { current = numeric; clearInterval(interval); }"
    kpi_html += '    const numStr = current.toLocaleString("en-IN");'
    kpi_html += "    el.textContent = suffix ? `₹${numStr}${suffix}` : `$${numStr}`;"
    kpi_html += "  }, 30);"
    kpi_html += "});"
    kpi_html += "</script>"
    st.components.v1.html(kpi_html, height=0)

    # 3 insight cards
    c1, c2, c3 = st.columns(3)
    insights = [
        (
            "📈 Log Transform Boost",
            "Log-transforming Price reduced skewness from **5.64 → -0.12**, boosting Linear Regression from R² 0.66 → **0.77**",
            "#e85d04",
        ),
        (
            "🏆 Top Predictor: car_age",
            "Car age is the strongest predictor (corr: **-0.78** with Price). Newer cars command much higher prices.",
            "#4895ef",
        ),
        (
            "💎 Luxury Premium",
            "Luxury brands (Audi, BMW, Mercedes) command **8× higher** prices than economy cars (Maruti, Datsun).",
            "#52b788",
        ),
    ]
    for col, (title, desc, color) in zip([c1, c2, c3], insights):
        with col:
            st.markdown(
                f'<div class="glass-card"><h3 style="color:{color};font-size:1.1rem;margin:0">{title}</h3>'
                f'<p style="color:#c8ccd4;font-size:0.9rem;margin-top:8px">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    # Pipeline timeline
    st.markdown("### 🔄 Pipeline Stages")
    stages = [
        "Raw CSV",
        "Dedup",
        "Feature Eng.",
        "Log Transform",
        "Scale",
        "Train/Test Split",
        "GridSearchCV",
        "Dashboard",
    ]
    cols = st.columns(len(stages))
    for i, (col, stage) in enumerate(zip(cols, stages)):
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:8px;background:{"rgba(232,93,4,0.1)" if i == len(stages) - 1 else "rgba(255,255,255,0.03)"};'
                f'border-radius:10px;border:1px solid {"#e85d04" if i == len(stages) - 1 else "rgba(255,255,255,0.06)"}">'
                f'<div style="font-size:1.2rem;font-weight:700;color:{"#e85d04" if i == len(stages) - 1 else "#c8ccd4"}">{i + 1}</div>'
                f'<div style="font-size:0.7rem;color:#8892a0">{stage}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Quick Predict widget
    st.markdown("### ⚡ Quick Predict")
    with st.container():
        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1:
            q_company = st.selectbox(
                "Brand",
                companies,
                key="qp_comp",
                index=companies.index("Maruti") if "Maruti" in companies else 0,
            )
        with qc2:
            q_year = st.slider("Year", 1996, 2024, 2018, key="qp_year")
        with qc3:
            q_kms = st.number_input("KMs", 0, 300000, 50000, key="qp_kms", step=1000)
        with qc4:
            q_fuel = st.selectbox("Fuel", fuel_types, key="qp_fuel", index=0)
        if st.button("🔮 Quick Estimate", key="qp_btn", use_container_width=True):
            with st.spinner("Predicting..."):
                input_df = pd.DataFrame(
                    [
                        {
                            "car_age": CURRENT_YEAR - q_year,
                            "kms_driven": q_kms,
                            "company": q_company,
                            "fuel_type_simple": get_fuel_simple(q_fuel),
                        }
                    ]
                )
                if "Linear Regression" in models:
                    pred = make_prediction(models["Linear Regression"], input_df, preprocessor)
                    tier, cls = get_price_tier(pred)
                    st.markdown(
                        f'<div class="glass-card" style="text-align:center;padding:20px">'
                        f'<h2 style="margin:0">Estimated Price: <span class="shimmer" style="font-size:2.2rem">{fmt_inr(pred)}</span></h2>'
                        f'<p style="color:#8892a0;margin:4px 0">Tier: <span class="{cls}">{tier}</span></p>'
                        f'<p style="color:#5a6270;font-size:0.8rem">Based on Linear Regression (R²=0.7654) | Confidence: ±₹2.5L</p>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )


# =========================================================================
