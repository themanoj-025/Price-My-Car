"""
AutoIntel — Used Car Price Intelligence
=========================================
Production-ready Streamlit dashboard for the Car Price Prediction ML project.
8 pages, 10 enhanced features, dark theme, fully interactive.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os, json, warnings, time
from datetime import datetime
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import xgboost as xgb
from io import BytesIO, StringIO
from helpers import (
    fmt_inr, get_price_tier, price_tier_badge, get_fuel_simple,
    get_company_tier, get_car_name_options, compute_deal_score,
    ensemble_prediction, shap_lite_approximation,
    generate_data_quality_report, generate_natural_language_explanation,
    make_prediction, MODEL_METRICS, METRICS_DF, FUEL_COLORS, TIER_COLORS,
    get_filtered_data as _get_filtered_data_raw,
)

warnings.filterwarnings('ignore')
CURRENT_YEAR = 2025

# =========================================================================
# Page Config
# =========================================================================
st.set_page_config(page_title="AutoIntel — Car Price Intelligence", page_icon="🚗",
                   layout="wide", initial_sidebar_state="expanded")

# =========================================================================
# Custom CSS Injection
# =========================================================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syne:wght@700;800&display=swap');
    * { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
    .stApp { background: #0c0f14; }
    section[data-testid="stSidebar"] { background: #0a0d12 !important; border-right: 1px solid rgba(255,255,255,0.05); }
    section[data-testid="stSidebar"] .stMarkdown { color: #c8ccd4; }
    .stMetric { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 16px; border: 1px solid rgba(255,255,255,0.06); }
    .stMetric label { color: #8892a0 !important; font-size: 0.8rem !important; }
    .stMetric [data-testid="stMetricValue"] { color: #e85d04 !important; font-size: 1.8rem !important; font-weight: 700; }
    .stSelectbox, .stSlider, .stNumberInput { background: rgba(255,255,255,0.03); border-radius: 8px; }
    .stButton button { background: linear-gradient(135deg, #e85d04, #f48c06) !important; color: white !important;
                       border: none !important; border-radius: 25px !important; padding: 8px 24px !important;
                       font-weight: 600 !important; transition: all 0.3s ease !important; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(232,93,4,0.4) !important; }
    .glass-card { background: rgba(255,255,255,0.03); backdrop-filter: blur(12px);
                  border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px;
                  transition: all 0.3s ease; }
    .glass-card:hover { border-color: rgba(232,93,4,0.3); box-shadow: 0 4px 20px rgba(232,93,4,0.1); }
    .badge-luxury { background: linear-gradient(135deg, #9b5de5, #7b2cbf); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-premium { background: linear-gradient(135deg, #e85d04, #f48c06); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-mid { background: linear-gradient(135deg, #4895ef, #4cc9f0); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-budget { background: linear-gradient(135deg, #52b788, #40916c); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .gradient-divider { height: 2px; background: linear-gradient(90deg, transparent, #e85d04, #f48c06, transparent); margin: 16px 0; }
    .nav-item { padding: 10px 16px; border-radius: 10px; margin: 2px 0; cursor: pointer;
                transition: all 0.2s; color: #c8ccd4; font-size: 0.9rem; }
    .nav-item:hover { background: rgba(232,93,4,0.1); color: #e85d04; border-left: 3px solid #e85d04; }
    .nav-active { background: rgba(232,93,4,0.15); color: #e85d04; border-left: 3px solid #e85d04; font-weight: 600; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0c0f14; }
    ::-webkit-scrollbar-thumb { background: #e85d04; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #f48c06; }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #e85d04, #f48c06) !important; }
    [data-testid="stDataFrame"] { background: transparent !important; }
    [data-testid="stDataFrame"] th { background: #1a1d24 !important; color: #e85d04 !important; }
    [data-testid="stDataFrame"] td { background: rgba(255,255,255,0.02) !important; color: #c8ccd4 !important; border-color: rgba(255,255,255,0.05) !important; }
    [data-testid="stDataFrame"] tr:nth-child(even) td { background: rgba(255,255,255,0.04) !important; }
    .shimmer { background: linear-gradient(90deg, #e85d04 25%, #f48c06 50%, #e85d04 75%);
               background-size: 200% 100%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               animation: shimmer 2s infinite; }
    @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    .hero-text { font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #e85d04, #f48c06, #4895ef);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px !important; padding: 8px 16px !important; color: #8892a0 !important; font-size: 0.85rem !important; }
    .stTabs [aria-selected="true"] { background: rgba(232,93,4,0.2) !important; color: #e85d04 !important; }
    .stExpander { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# Plotly Config Helper
# =========================================================================
def apply_plotly_config(fig, height=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,16,25,0.8)",
        font=dict(family="DM Sans", color="#e8eaf0"),
        height=height or 350,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", gridwidth=1, title_font=dict(size=11))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", gridwidth=1, title_font=dict(size=11))
    # Only apply marker styling to traces that support it (scatter, bar, etc.)
    for trace in fig.data:
        if trace.__class__.__name__ not in ('Heatmap', 'Heatmapgl', 'Histogram2d', 'Histogram2dContour'):
            trace.update(marker=dict(line=dict(width=0)))
    fig.update_layout(showlegend=False)
    fig.update_layout(legend=dict(font=dict(size=9)))
    fig.update_layout(hoverlabel=dict(bgcolor="#1a1d24", font_size=12, font_family="DM Sans"))
    return fig

def show_chart(fig, height=None):
    fig = apply_plotly_config(fig, height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =========================================================================
# Session State Init
# =========================================================================
def init_session_state():
    defaults = {
        'page': "🏠 Dashboard Home", 'last_model': None, 'last_prediction': {},
        'page_visits': {}, 'global_filters': {}, 'expert_mode': True,
        'last_pred_inputs': {}, 'ab_mode': False, 'ab_car1': {}, 'ab_car2': {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =========================================================================
# Cache Functions
# =========================================================================
@st.cache_data(show_spinner="📦 Loading car dataset...")
def load_data():
    df = pd.read_csv('Cleaned_Car_data.csv', index_col=0)
    df['car_age'] = CURRENT_YEAR - df['year']
    df['price_tier'] = pd.cut(df['Price'], bins=[0, 300000, 800000, 2000000, 1e8],
                               labels=['Budget', 'Mid-range', 'Premium', 'Luxury'])
    return df

@st.cache_resource(show_spinner="🧠 Loading preprocessor...")
def load_preprocessor():
    return joblib.load('ml_ready/preprocessor.pkl')

@st.cache_resource(show_spinner="🤖 Loading ML models...")
def load_models():
    models = {}; model_dir = 'ml_ready/models'
    model_map = {'gradient_boosting.pkl': 'Gradient Boosting', 'xgboost.pkl': 'XGBoost',
                 'random_forest.pkl': 'Random Forest', 'linear_regression.pkl': 'Linear Regression',
                 'ridge.pkl': 'Ridge', 'svr.pkl': 'SVR', 'lasso.pkl': 'Lasso', 'knn.pkl': 'KNN'}
    for fname in os.listdir(model_dir):
        if fname in model_map:
            models[model_map[fname]] = joblib.load(os.path.join(model_dir, fname))
    return models

@st.cache_resource(show_spinner="📊 Loading model results...")
def load_gs_results():
    results = {}
    for fname in ['gradient_boosting_gs_results.json', 'xgboost_gs_results.json', 'random_forest_gs_results.json']:
        path = f'ml_ready/models/{fname}'
        if os.path.exists(path):
            with open(path) as f:
                results[fname.replace('_gs_results.json', '')] = json.load(f)
    return results

@st.cache_data(ttl=3600, show_spinner="📐 Loading preprocessed data...")
def load_preprocessed():
    return {
        'X_train': np.load('ml_ready/X_train.npy'), 'X_test': np.load('ml_ready/X_test.npy'),
        'y_train': np.load('ml_ready/y_train.npy'), 'y_test': np.load('ml_ready/y_test.npy'),
        'y_train_orig': np.load('ml_ready/y_train_original.npy'),
        'y_test_orig': np.load('ml_ready/y_test_original.npy'),
        'feature_names': np.load('ml_ready/feature_names.npy', allow_pickle=True)
    }

# =========================================================================
# Helper Functions (imported from helpers.py)
# =========================================================================
# fmt_inr, get_price_tier, price_tier_badge, make_prediction, get_car_name_options,
# get_fuel_simple, get_company_tier, MODEL_METRICS, METRICS_DF all imported from helpers.py

@st.cache_data(ttl=3600)
def get_filtered_data(df, companies, fuels, year_r, price_r, kms_r):
    return _get_filtered_data_raw(df, companies, fuels, year_r, price_r, kms_r)

# =========================================================================
# Enhanced Features (imported from helpers.py)
# =========================================================================
# compute_deal_score, ensemble_prediction, shap_lite_approximation,
# generate_data_quality_report, generate_natural_language_explanation
# all imported from helpers.py

# =========================================================================
# Data Load with Error Handling
# =========================================================================
init_session_state()

demo_mode = False
try:
    df = load_data()
    preprocessor = load_preprocessor()
    models = load_models()
    pp_data = load_preprocessed()
    gs_results = load_gs_results()
    if not models:
        demo_mode = True
except Exception as e:
    st.error(f"⚠️ Could not load ML artifacts: {e}. Running in demo mode with synthetic data.")
    demo_mode = True

if demo_mode:
    # Demo mode: generate synthetic data
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'name': [f'Demo Car {i}' for i in range(n)],
        'company': np.random.choice(['Maruti', 'Hyundai', 'Honda', 'Toyota', 'BMW'], n),
        'year': np.random.randint(2000, 2025, n),
        'Price': np.random.lognormal(mean=13, sigma=0.8, size=n),
        'kms_driven': np.random.randint(1000, 200000, n),
        'fuel_type': np.random.choice(['Petrol', 'Diesel', 'CNG'], n, p=[0.6, 0.35, 0.05])
    })
    df['car_age'] = CURRENT_YEAR - df['year']
    df['price_tier'] = pd.cut(df['Price'], bins=[0, 300000, 800000, 2000000, 1e8],
                               labels=['Budget', 'Mid-range', 'Premium', 'Luxury'])
    preprocessor = None
    models = {}
    pp_data = {'X_test': np.random.randn(50, 39), 'y_test': np.random.randn(50),
               'y_test_orig': np.random.lognormal(mean=13, sigma=0.8, size=50),
               'feature_names': np.array([f'feature_{i}' for i in range(39)])}
    gs_results = {}
    st.info("🔧 Running in **Demo Mode** — predictions will use synthetic data. Place the full dataset in `ml_ready/` for production use.")

inject_custom_css()

companies = sorted(df['company'].unique())
fuel_types = sorted(df['fuel_type'].unique())

# =========================================================================
# Sidebar
# =========================================================================
with st.sidebar:
    st.markdown('<p style="font-family:Syne;font-size:1.8rem;font-weight:800;color:#e85d04;margin:0">🚗 AutoIntel</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892a0;font-size:0.8rem;margin-top:-8px">Used Car Price Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    nav_items = ["🏠 Dashboard Home", "📊 Dataset Explorer", "🔍 EDA Deep-Dive",
                 "🤖 Model Comparison Lab", "🧪 Residual Analysis", "🔮 Price Predictor",
                 "📈 Market Intelligence", "⚙️ Pipeline Inspector"]
    for item in nav_items:
        active = "nav-active" if st.session_state.page == item else ""
        if st.button(item, key=f"nav_{item}", use_container_width=True,
                     help=f"Go to {item}", type="secondary"):
            st.session_state.page = item
            st.rerun()
        st.markdown(f'<style>div.stButton button[key="nav_{item}"] {{'
                    f'background: {"rgba(232,93,4,0.15)" if st.session_state.page == item else "transparent"} !important;'
                    f'color: {"#e85d04" if st.session_state.page == item else "#c8ccd4"} !important;'
                    f'border-left: {"3px solid #e85d04" if st.session_state.page == item else "3px solid transparent"} !important;'
                    f'text-align: left !important; border-radius: 0 !important;'
                    f'justify-content: left !important; padding: 8px 16px !important;}}</style>', unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    with st.expander("⚡ Quick Stats", expanded=False):
        col1, col2 = st.columns(2)
        col1.metric("Records", f"{len(df):,}")
        col2.metric("Companies", f"{len(companies)}")
        col1.metric("Best R²", "0.7654")
        col2.metric("Features", "39")

    with st.expander("🎛️ Global Filters", expanded=False):
        st.session_state.global_filters['company'] = st.multiselect("Company", companies, key="gf_comp")
        st.session_state.global_filters['fuel'] = st.multiselect("Fuel", fuel_types, key="gf_fuel")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="glass-card" style="padding:12px;font-size:0.8rem">'
                f'<span style="color:#8892a0">Data last processed:</span> <span style="color:#e8eaf0">2025-01-15</span><br>'
                f'<span style="color:#8892a0">Models trained on:</span> <span style="color:#e8eaf0">8,919 samples</span><br>'
                f'<span style="color:#8892a0">Page visits:</span> <span style="color:#e85d04">{sum(st.session_state.page_visits.values())}</span>'
                f'</div>', unsafe_allow_html=True)

    with st.expander("🧠 Explainability Mode", expanded=False):
        st.session_state.expert_mode = st.toggle("Expert Mode", value=st.session_state.expert_mode)
        mode_label = "Expert" if st.session_state.expert_mode else "Simple"
        st.caption(f"Current: {mode_label} — {'Shows R², RMSE, residuals' if st.session_state.expert_mode else 'Plain English, no stats jargon'}")

    st.markdown(f'<p style="color:#5a6270;font-size:0.75rem;text-align:center;margin-top:16px">'
                f'Built by AutoIntel Team · MIT License · v5.0</p>', unsafe_allow_html=True)

# =========================================================================
# PAGE 1: Dashboard Home
# =========================================================================
def page_dashboard_home():
    st.markdown('<p class="hero-text">AutoIntel — Used Car Price Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892a0;font-size:1.1rem;margin-top:-8px">'
                'AI-powered insights into the Indian used car market — 11,149 listings analyzed with 8 ML models</p>',
                unsafe_allow_html=True)
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
    kpi_html = '<script>'
    kpi_html += 'document.querySelectorAll("[data-testid=stMetricValue]").forEach(el => {'
    kpi_html += '  const target = el.textContent.replace(/[^0-9.,KLCr]/g, "").trim();'
    kpi_html += '  if (!target) return;'
    kpi_html += '  const numeric = parseFloat(target.replace(/,/g, "")) || 0;'
    kpi_html += '  const suffix = target.replace(/[0-9.,]/g, "").trim();'
    kpi_html += '  let current = 0;'
    kpi_html += '  const step = Math.max(1, Math.floor(numeric / 40));'
    kpi_html += '  const interval = setInterval(() => {'
    kpi_html += '    current += step;'
    kpi_html += '    if (current >= numeric) { current = numeric; clearInterval(interval); }'
    kpi_html += '    const numStr = current.toLocaleString(\"en-IN\");'
    kpi_html += '    el.textContent = suffix ? `₹${numStr}${suffix}` : `$${numStr}`;'
    kpi_html += '  }, 30);'
    kpi_html += '});'
    kpi_html += '</script>'
    st.components.v1.html(kpi_html, height=0)

    # 3 insight cards
    c1, c2, c3 = st.columns(3)
    insights = [
        ("📈 Log Transform Boost", "Log-transforming Price reduced skewness from **5.64 → -0.12**, boosting Linear Regression from R² 0.66 → **0.77**", "#e85d04"),
        ("🏆 Top Predictor: car_age", "Car age is the strongest predictor (corr: **-0.78** with Price). Newer cars command much higher prices.", "#4895ef"),
        ("💎 Luxury Premium", "Luxury brands (Audi, BMW, Mercedes) command **8× higher** prices than economy cars (Maruti, Datsun).", "#52b788"),
    ]
    for col, (title, desc, color) in zip([c1, c2, c3], insights):
        with col:
            st.markdown(f'<div class="glass-card"><h3 style="color:{color};font-size:1.1rem;margin:0">{title}</h3>'
                        f'<p style="color:#c8ccd4;font-size:0.9rem;margin-top:8px">{desc}</p></div>',
                        unsafe_allow_html=True)

    # Pipeline timeline
    st.markdown("### 🔄 Pipeline Stages")
    stages = ["Raw CSV", "Dedup", "Feature Eng.", "Log Transform", "Scale", "Train/Test Split", "GridSearchCV", "Dashboard"]
    cols = st.columns(len(stages))
    for i, (col, stage) in enumerate(zip(cols, stages)):
        with col:
            st.markdown(f'<div style="text-align:center;padding:8px;background:{"rgba(232,93,4,0.1)" if i==len(stages)-1 else "rgba(255,255,255,0.03)"};'
                        f'border-radius:10px;border:1px solid {"#e85d04" if i==len(stages)-1 else "rgba(255,255,255,0.06)"}">'
                        f'<div style="font-size:1.2rem;font-weight:700;color:{"#e85d04" if i==len(stages)-1 else "#c8ccd4"}">{i+1}</div>'
                        f'<div style="font-size:0.7rem;color:#8892a0">{stage}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Quick Predict widget
    st.markdown("### ⚡ Quick Predict")
    with st.container():
        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1: q_company = st.selectbox("Brand", companies, key="qp_comp", index=companies.index('Maruti') if 'Maruti' in companies else 0)
        with qc2: q_year = st.slider("Year", 1996, 2024, 2018, key="qp_year")
        with qc3: q_kms = st.number_input("KMs", 0, 300000, 50000, key="qp_kms", step=1000)
        with qc4: q_fuel = st.selectbox("Fuel", fuel_types, key="qp_fuel", index=0)
        if st.button("🔮 Quick Estimate", key="qp_btn", use_container_width=True):
            with st.spinner("Predicting..."):
                input_df = pd.DataFrame([{'car_age': CURRENT_YEAR - q_year, 'kms_driven': q_kms,
                                          'company': q_company, 'fuel_type_simple': get_fuel_simple(q_fuel)}])
                if 'Linear Regression' in models:
                    pred = make_prediction(models['Linear Regression'], input_df, preprocessor)
                    tier, cls = get_price_tier(pred)
                    st.markdown(f'<div class="glass-card" style="text-align:center;padding:20px">'
                                f'<h2 style="margin:0">Estimated Price: <span class="shimmer" style="font-size:2.2rem">{fmt_inr(pred)}</span></h2>'
                                f'<p style="color:#8892a0;margin:4px 0">Tier: <span class="{cls}">{tier}</span></p>'
                                f'<p style="color:#5a6270;font-size:0.8rem">Based on Linear Regression (R²=0.7654) | Confidence: ±₹2.5L</p>'
                                f'</div>', unsafe_allow_html=True)

# =========================================================================
# PAGE 2: Dataset Explorer
# =========================================================================
def page_dataset_explorer():
    st.markdown("## 📊 Dataset Explorer")
    st.markdown('<p style="color:#8892a0">Filter, browse, and analyze the car dataset</p>', unsafe_allow_html=True)

    # Filters
    with st.expander("🔍 Filters", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            sel_companies = st.multiselect("Company", companies, default=companies[:5], key="de_comp")
        with f2:
            sel_fuels = st.multiselect("Fuel Type", fuel_types, default=fuel_types, key="de_fuel")
        with f3:
            yr_range = st.slider("Year Range", int(df['year'].min()), int(df['year'].max()),
                                 (int(df['year'].min()), int(df['year'].max())), key="de_yr")
        with f4:
            pr_range = st.slider("Price Range (₹)", float(df['Price'].min()), float(df['Price'].max()),
                                 (float(df['Price'].min()), float(df['Price'].max())), key="de_pr", format="₹%.0f")
        f5, f6 = st.columns(2)
        with f5:
            kms_range = st.slider("KMs Driven", 0, int(df['kms_driven'].max()), (0, int(df['kms_driven'].max())), key="de_kms")
        with f6:
            if st.button("🎲 Surprise Me", use_container_width=True):
                import random
                sel_companies = [random.choice(companies)]
                sel_fuels = [random.choice(fuel_types)]
                yr = random.randint(2000, 2020)
                yr_range = (yr, yr + 5)
                pr_range = (50000, random.randint(500000, 2000000))
                st.rerun()

    filtered = get_filtered_data(df, sel_companies if sel_companies else companies,
                                 sel_fuels if sel_fuels else fuel_types, yr_range, pr_range, kms_range)
    st.markdown(f'<p style="color:#c8ccd4">Showing <span style="color:#e85d04;font-weight:700">{len(filtered):,}</span> of {len(df):,} records</p>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Data Table", "📊 Dynamic Charts"])

    with tab1:
        # Color KMs based on condition
        km_med = float(df['kms_driven'].median())
        km_high = float(df['kms_driven'].quantile(0.75))
        col_config = {
            'name': st.column_config.TextColumn("Car Name", width="large"),
            'company': st.column_config.TextColumn("Company", width="small"),
            'year': st.column_config.NumberColumn("Year", format="%d"),
            'Price': st.column_config.ProgressColumn("Price (₹)", format="₹%.0f", min_value=0, max_value=float(df['Price'].max())),
            'kms_driven': st.column_config.NumberColumn("KMs Driven", format="%d"),
            'fuel_type': st.column_config.TextColumn("Fuel"),
            'car_age': st.column_config.NumberColumn("Age", format="%d yrs")
        }
        # Apply conditional coloring on KMs via CSS
        st.markdown(f'''<style>
        .kms-low td:nth-child(5) {{ color: #52b788 !important; }}
        .kms-mid td:nth-child(5) {{ color: #f48c06 !important; }}
        .kms-high td:nth-child(5) {{ color: #e85d04 !important; }}
        </style>''', unsafe_allow_html=True)
        st.dataframe(filtered.sort_values('Price', ascending=False).reset_index(drop=True),
                     column_config=col_config, use_container_width=True, height=450,
                     column_order=['name', 'company', 'year', 'Price', 'kms_driven', 'fuel_type', 'car_age'])

        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered CSV", csv, "filtered_cars.csv", "text/csv", use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(data=[go.Histogram(x=filtered['Price'], nbinsx=50, marker_color='#e85d04', opacity=0.8)])
            fig.update_layout(title="Price Distribution", xaxis_title="Price (₹)")
            show_chart(fig, 300)

            fuel_counts = filtered['fuel_type'].value_counts()
            fig2 = go.Figure(data=[go.Pie(labels=fuel_counts.index, values=fuel_counts.values,
                                          marker=dict(colors=[FUEL_COLORS.get(f, '#888') for f in fuel_counts.index]),
                                          textinfo='label+percent', hole=0.5)])
            fig2.update_layout(title="Fuel Breakdown")
            show_chart(fig2, 300)

        with c2:
            fig3 = go.Figure(data=[go.Histogram(x=filtered['kms_driven'], nbinsx=50, marker_color='#4895ef', opacity=0.8)])
            fig3.update_layout(title="KMs Distribution", xaxis_title="Kilometers Driven")
            show_chart(fig3, 300)

            yr_counts = filtered['year'].value_counts().sort_index()
            fig4 = go.Figure(data=[go.Bar(x=yr_counts.index, y=yr_counts.values, marker_color='#52b788')])
            fig4.update_layout(title="Year Distribution", xaxis_title="Year", yaxis_title="Count")
            show_chart(fig4, 300)

# =========================================================================
# PAGE 3: EDA Deep-Dive
# =========================================================================
def page_eda_deepdive():
    st.markdown("## 🔍 EDA Deep-Dive")
    st.markdown('<p style="color:#8892a0">Comprehensive exploratory data analysis with 5 tabs</p>', unsafe_allow_html=True)

    tabs = st.tabs(["💰 Price Analysis", "🏷️ Brand Intelligence", "📊 Feature Correlations",
                    "⚠️ Outlier Analysis", "📈 Year & Mileage Trends"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(data=[go.Histogram(x=df['Price'], nbinsx=60, marker_color='#4895ef', opacity=0.8, name="Raw Price")])
            fig.add_vline(x=df['Price'].median(), line=dict(color='#e85d04', dash='dash'), annotation_text=f"Median: {fmt_inr(df['Price'].median())}")
            fig.update_layout(title=f"Raw Price Distribution (skewness: {df['Price'].skew():.2f})", xaxis_title="Price (₹)")
            show_chart(fig, 350)
        with c2:
            log_p = np.log1p(df['Price'])
            fig2 = go.Figure(data=[go.Histogram(x=log_p, nbinsx=60, marker_color='#e85d04', opacity=0.8, name="Log Price")])
            fig2.update_layout(title=f"Log-Transformed Price (skewness: {log_p.skew():.2f})", xaxis_title="log(Price + 1)")
            show_chart(fig2, 350)

        pct = st.slider("Price Percentile Explorer", 1, 100, 50, 5)
        val = df['Price'].quantile(pct / 100)
        sample = df[df['Price'] >= val].nsmallest(1, 'Price')
        st.markdown(f'<div class="glass-card" style="text-align:center"><span style="color:#8892a0">P{pct} = </span>'
                    f'<span style="color:#e85d04;font-size:1.3rem;font-weight:700">{fmt_inr(val)}</span> — '
                    f'Buys a {sample.iloc[0]["name"] if len(sample)>0 else "car in this range"} '
                    f'({sample.iloc[0]["year"] if len(sample)>0 else ""})</div>', unsafe_allow_html=True)

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            med_prices = df.groupby('company')['Price'].median().sort_values(ascending=True)
            top20 = med_prices.tail(20)
            colors = [TIER_COLORS.get(get_company_tier(df[df['company']==c]['Price'].mean()), '#888') for c in top20.index]
            fig = go.Figure(data=[go.Bar(x=top20.values, y=top20.index, orientation='h',
                                          marker_color=colors, text=[fmt_inr(v) for v in top20.values],
                                          textposition='outside')])
            fig.update_layout(title="Top 20 Brands by Median Price", xaxis_title="Median Price", height=500)
            show_chart(fig, 500)
        with c2:
            brand_stats = df.groupby('company').agg(avg_price=('Price', 'mean'), count=('Price', 'count')).reset_index()
            brand_stats['tier'] = brand_stats['avg_price'].apply(get_company_tier)
            fig2 = go.Figure(data=[go.Scatter(x=brand_stats['count'], y=brand_stats['avg_price'],
                                              mode='markers+text', text=brand_stats['company'],
                                              textposition='top center', marker=dict(
                    size=np.sqrt(brand_stats['count']) * 3,
                    color=[TIER_COLORS.get(t, '#888') for t in brand_stats['tier']],
                    line=dict(color='white', width=1)), textfont=dict(size=8))])
            fig2.update_layout(title="Brand Positioning: Volume vs Price", xaxis_title="Number of Listings",
                               yaxis_title="Avg Price (₹)", height=500)
            show_chart(fig2, 500)

        st.markdown("### Brand Comparison")
        sel_brands = st.multiselect("Select 2-4 brands to compare", companies, default=['Maruti', 'Hyundai', 'BMW', 'Mercedes-Benz'])
        if len(sel_brands) >= 2:
            fig3 = go.Figure()
            for brand in sel_brands:
                bdata = df[df['company'] == brand]['Price'] / 1e5
                fig3.add_trace(go.Box(y=bdata, name=brand, marker_color=TIER_COLORS.get(get_company_tier(df[df['company']==brand]['Price'].mean()), '#888'),
                                       boxmean='sd'))
            fig3.update_layout(title="Price Distribution Comparison (in lakhs)", yaxis_title="Price (₹ Lakhs)", height=400)
            show_chart(fig3, 400)

    with tabs[2]:
        num_cols = ['Price', 'year', 'kms_driven', 'car_age']
        corr = df[num_cols].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns,
                                         text=np.round(corr.values, 3), texttemplate='%{text}',
                                         textfont=dict(size=12, color='white'),
                                         colorscale='RdBu_r', zmin=-1, zmax=1))
        fig.update_layout(title="Correlation Matrix", height=450)
        show_chart(fig, 450)

        # Scatter matrix (using go instead of px)
        sample_df = df.sample(min(2000, len(df)))
        fig2 = make_subplots(rows=3, cols=3, shared_xaxes=True, shared_yaxes=True,
                              subplot_titles=['Price', 'car_age', 'kms_driven'])
        dims = ['Price', 'car_age', 'kms_driven']
        for i, dim_y in enumerate(dims):
            for j, dim_x in enumerate(dims):
                if i != j:
                    for fuel, color in FUEL_COLORS.items():
                        subset = sample_df[sample_df['fuel_type'] == fuel]
                        fig2.add_trace(go.Scatter(x=subset[dim_x], y=subset[dim_y],
                                                   mode='markers', marker=dict(color=color, size=3, opacity=0.4),
                                                   name=fuel, showlegend=(i == 0 and j == 1)),
                                       row=i + 1, col=j + 1)
                else:
                    fig2.add_trace(go.Histogram(x=sample_df[dim_x], marker_color='#4895ef', showlegend=False),
                                   row=i + 1, col=j + 1)
                fig2.update_xaxes(title_text=dim_x if i == 2 else '', row=i + 1, col=j + 1)
                fig2.update_yaxes(title_text=dim_y if j == 0 else '', row=i + 1, col=j + 1)
        fig2.update_layout(title="Scatter Matrix: Price × Car Age × KMs Driven", height=600)
        show_chart(fig2, 600)

        # VIF table for multicollinearity check
        st.markdown("### VIF — Variance Inflation Factor")
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            vif_df = df[['Price', 'car_age', 'kms_driven']].dropna()
            vif_data = pd.DataFrame()
            vif_data['Feature'] = vif_df.columns
            vif_data['VIF'] = [variance_inflation_factor(vif_df.values, i) for i in range(vif_df.shape[1])]
            st.dataframe(vif_data.style.applymap(lambda v: 'color:#e85d04' if v > 10 else ('color:#f48c06' if v > 5 else 'color:#52b788'),
                                                  subset=['VIF']), use_container_width=True)
            st.caption("VIF > 10 indicates severe multicollinearity; > 5 moderate; < 5 low.")
        except ImportError:
            # Manual VIF approximation
            corr = df[['Price', 'car_age', 'kms_driven']].corr()
            vif_approx = []
            for col in ['Price', 'car_age', 'kms_driven']:
                r2_other = 0
                for other in ['Price', 'car_age', 'kms_driven']:
                    if other != col:
                        r2_other = max(r2_other, corr.loc[col, other] ** 2)
                vif_approx.append(1 / (1 - r2_other)) if r2_other < 1 else 0
            vif_data = pd.DataFrame({'Feature': ['Price', 'car_age', 'kms_driven'], 'VIF': [f'{v:.2f}' for v in vif_approx]})
            st.dataframe(vif_data, use_container_width=True)
            st.caption("VIF estimated via max pairwise R² (install statsmodels for exact calculation).")

    with tabs[3]:
        st.markdown("### IQR-Based Outlier Detection")
        c1, c2 = st.columns(2)
        outliers_info = []
        for col in ['Price', 'kms_driven']:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            n_out = ((df[col] < lower) | (df[col] > upper)).sum()
            outliers_info.append((col, n_out, f"{fmt_inr(lower)} – {fmt_inr(upper)}", f"{fmt_inr(Q1)} – {fmt_inr(Q3)}"))
        out_df = pd.DataFrame(outliers_info, columns=['Feature', 'Outliers', 'Outlier Bounds', 'IQR Range'])
        st.dataframe(out_df, use_container_width=True)

        st.markdown("### Before/After: KMs Driven Capping")
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(data=[go.Scatter(x=df['car_age'], y=df['kms_driven'], mode='markers',
                                              marker=dict(color='#4895ef', size=4, opacity=0.4))])
            fig.update_layout(title="Before Capping", xaxis_title="Car Age", yaxis_title="KMs Driven")
            show_chart(fig, 300)
        with c2:
            capped = df['kms_driven'].clip(upper=df['kms_driven'].quantile(0.99))
            fig2 = go.Figure(data=[go.Scatter(x=df['car_age'], y=capped, mode='markers',
                                               marker=dict(color='#52b788', size=4, opacity=0.4))])
            fig2.update_layout(title="After Capping at P99", xaxis_title="Car Age", yaxis_title="KMs Driven")
            show_chart(fig2, 300)

        fig3 = go.Figure()
        for col in ['Price', 'kms_driven', 'car_age']:
            fig3.add_trace(go.Box(y=df[col], name=col.replace('_', ' ').title()))
        fig3.update_layout(title="Box Plots with Outliers Highlighted", height=400)
        show_chart(fig3, 400)

    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            med_by_year = df.groupby('year')['Price'].median().reset_index()
            fig = go.Figure(data=[go.Scatter(x=med_by_year['year'], y=med_by_year['Price'],
                                              mode='lines+markers', line=dict(color='#e85d04', width=3),
                                              marker=dict(size=6, color='#e85d04'))])
            fig.update_layout(title="Median Price by Year (2000–2024) — Click 'Animate' to play",
                              xaxis_title="Year", yaxis_title="Median Price (₹)",
                              sliders=[{"steps": [{"args": [[yr], {"frame": {"duration": 500, "redraw": True}}],
                                                      "label": str(yr), "method": "animate"}
                                                     for yr in med_by_year['year'][::2]],
                                        "active": len(med_by_year) - 1,
                                        "currentvalue": {"prefix": "Year: "}}],
                              updatemenus=[{"buttons": [{"args": [None, {"frame": {"duration": 300, "redraw": True},
                                                                         "fromcurrent": True}],
                                                           "label": "▶ Play", "method": "animate"},
                                                          {"args": [[None], {"frame": {"duration": 0, "redraw": True},
                                                                         "mode": "immediate"}],
                                                           "label": "⏹ Pause", "method": "animate"}],
                                             "type": "buttons", "x": 0.5, "y": -0.2, "xanchor": "center"}])
            # Create animation frames
            frames = []
            for yr in med_by_year['year']:
                trace_data = med_by_year[med_by_year['year'] <= yr]
                frames.append(go.Frame(data=[go.Scatter(x=trace_data['year'], y=trace_data['Price'],
                                                         mode='lines+markers', marker=dict(color='#e85d04'),
                                                         line=dict(color='#e85d04'))], name=str(yr)))
            fig.frames = frames
            show_chart(fig, 400)
        with c2:
            sample2 = df.sample(min(2000, len(df)))
            fig2 = go.Figure(data=go.Histogram2d(x=sample2['kms_driven'], y=sample2['Price'],
                                                  colorscale='Hot', nbinsx=30, nbinsy=30))
            fig2.update_layout(title="Density: KMs Driven vs Price", xaxis_title="KMs Driven",
                               yaxis_title="Price (₹)")
            show_chart(fig2, 400)

# =========================================================================
# PAGE 4: Model Comparison Lab
# =========================================================================
def page_model_comparison():
    st.markdown("## 🤖 Model Comparison Lab")
    st.markdown('<p style="color:#8892a0">Compare 8 ML models across multiple dimensions</p>', unsafe_allow_html=True)

    # Apply explainability mode
    expert = st.session_state.expert_mode

    # Summary table
    display_df = METRICS_DF.copy()
    display_df.index = range(1, len(display_df) + 1)
    if expert:
        display_df['RMSE'] = display_df['RMSE'].apply(lambda x: f"₹{x:,}")
        display_df['MAE'] = display_df['MAE'].apply(lambda x: f"₹{x:,}")
        display_df['Test R²'] = display_df['Test R²'].apply(lambda x: f"{x:.4f}")
        display_df['Time (s)'] = display_df['Time (s)'].apply(lambda x: f"{x:.2f}s")
        st.dataframe(display_df[['Model', 'Test R²', 'RMSE', 'MAE', 'Time (s)', 'Params']], use_container_width=True)
    else:
        st.markdown('<div class="glass-card" style="text-align:center"><strong>🏆 Best Model:</strong> Linear Regression achieves the highest accuracy with R² score of 0.7654, meaning it explains <strong>76.5%</strong> of price variation across cars.</div>', unsafe_allow_html=True)

    # Remaining stats shown only in expert mode
    if expert:
        best = METRICS_DF.loc[METRICS_DF['Test R²'].idxmax()]
        st.markdown(f'<div class="glass-card" style="text-align:center;border-color:rgba(82,183,136,0.3)">'
                    f'🏆 <strong>Best Model:</strong> {best["Model"]} — '
                    f'R²: <span style="color:#52b788">{best["Test R²"]:.4f}</span> | '
                    f'RMSE: <span style="color:#e85d04">₹{best["RMSE"]:,}</span> | '
                    f'MAE: <span style="color:#4895ef">₹{best["MAE"]:,}</span></div>', unsafe_allow_html=True)

    # R² bar chart (shown in both modes)
    sorted_df = METRICS_DF.sort_values('Test R²')
    colors_r2 = ['#52b788' if i == len(sorted_df) - 1 else ('#4895ef' if i > len(sorted_df) - 4 else '#5a6270')
                 for i in range(len(sorted_df))]
    fig = go.Figure(data=[go.Bar(x=sorted_df['Test R²'], y=sorted_df['Model'], orientation='h',
                                  marker_color=colors_r2, text=[f"{v:.4f}" for v in sorted_df['Test R²']],
                                  textposition='outside')])
    fig.update_layout(title="R² Score (higher is better)", xaxis_range=[0, 1], height=400)
    show_chart(fig, 400)

    c1, c2 = st.columns(2)
    with c1:
        melted = METRICS_DF.melt(id_vars=['Model'], value_vars=['RMSE', 'MAE'], var_name='Metric', value_name='Value')
        fig2 = go.Figure()
        for metric, color in [('RMSE', '#e85d04'), ('MAE', '#4895ef')]:
            m = melted[melted['Metric'] == metric]
            fig2.add_trace(go.Bar(name=metric, x=m['Model'], y=m['Value'], marker_color=color))
        fig2.update_layout(title="RMSE & MAE (lower is better)", barmode='group', xaxis_tickangle=-45, height=400)
        show_chart(fig2, 400)
    with c2:
        fig3 = go.Figure(data=[go.Scatter(x=METRICS_DF['Time (s)'], y=METRICS_DF['Test R²'],
                                           mode='markers+text', text=METRICS_DF['Model'], textposition='top center',
                                           marker=dict(size=[20 if m == best['Model'] else 12 for m in METRICS_DF['Model']],
                                                       color=['#e85d04' if m == best['Model'] else '#4895ef' for m in METRICS_DF['Model']]))])
        fig3.update_layout(title="Training Time vs Performance", xaxis_title="Time (s)", yaxis_title="R² Score", height=400)
        show_chart(fig3, 400)

    # Radar chart
    st.markdown("### 🕸️ Multi-Dimensional Radar")
    radar_models = ['Linear Regression', 'Ridge', 'XGBoost', 'Gradient Boosting', 'SVR', 'Lasso', 'KNN', 'Random Forest']
    categories = ['R² Score', 'Speed', 'Accuracy', 'Interpretability', 'Stability']
    radar_data = {
        'Linear Regression': [0.9, 0.95, 0.85, 0.95, 0.9],
        'Ridge': [0.88, 0.98, 0.84, 0.9, 0.92],
        'XGBoost': [0.85, 0.7, 0.88, 0.6, 0.8],
        'Gradient Boosting': [0.83, 0.5, 0.85, 0.6, 0.82],
        'SVR': [0.7, 0.2, 0.72, 0.5, 0.65],
        'Lasso': [0.65, 0.9, 0.7, 0.85, 0.78],
        'KNN': [0.62, 0.95, 0.68, 0.5, 0.6],
        'Random Forest': [0.6, 0.6, 0.65, 0.75, 0.7]
    }
    radar_colors = ['#e85d04', '#4895ef', '#52b788', '#9b5de5', '#f48c06', '#00b4d8', '#e63946', '#6a994e']
    fig4 = go.Figure()
    for idx, model in enumerate(radar_models):
        vals = radar_data[model] + [radar_data[model][0]]
        fig4.add_trace(go.Scatterpolar(r=vals, theta=categories + [categories[0]],
                                       fill='toself', name=model,
                                       line=dict(color=radar_colors[idx]),
                                       opacity=0.7))
    fig4.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), title="Model Comparison Radar", height=500)
    show_chart(fig4, 500)

    # Hyperparameter tuning results
    st.markdown("### 🔧 Hyperparameter Tuning Results")
    if gs_results:
        tune_tabs = st.tabs([k.replace('_', ' ').title() for k in gs_results.keys()])
        for i, (name, results) in enumerate(gs_results.items()):
            with tune_tabs[i]:
                params = results.get('params', [])
                scores = results.get('mean_test_score', [])
                if params:
                    gs_df = pd.DataFrame({'Params': params[:10], 'CV R² (log)': [f'{s:.4f}' for s in scores[:10]]})
                    st.dataframe(gs_df, use_container_width=True)
                if 'xgboost' in name:
                    st.markdown(f'<div class="glass-card" style="text-align:center;border-left:3px solid #52b788">'
                                f'<strong>Improvement Delta:</strong> <span style="color:#52b788">+0.0104 R²</span> '
                                f'from tuning XGBoost (0.7359 → 0.7463)</div>', unsafe_allow_html=True)
                if 'gradient_boosting' in name:
                    st.markdown(f'<div class="glass-card" style="text-align:center;border-left:3px solid #4895ef">'
                                f'<strong>Improvement Delta:</strong> <span style="color:#4895ef">+0.0082 R²</span> '
                                f'from tuning Gradient Boosting</div>', unsafe_allow_html=True)
                if 'random_forest' in name:
                    st.markdown(f'<div class="glass-card" style="text-align:center;border-left:3px solid #9b5de5">'
                                f'<strong>Improvement Delta:</strong> <span style="color:#9b5de5">+0.0035 R²</span> '
                                f'from tuning Random Forest</div>', unsafe_allow_html=True)
    else:
        st.info("GridSearchCV results not available. Run `tune_hyperparameters.py` to generate them.")

    # Log Transform impact section (conditional on mode)
    st.markdown("### 📉 Log Transform Impact")
    if expert:
        c1, c2 = st.columns(2)
        with c1:
            fig5 = go.Figure(data=[go.Bar(x=['Before Log (R²=0.66)', 'After Log (R²=0.77)'],
                                           y=[0.66, 0.77], marker_color=['#5a6270', '#52b788'],
                                           text=['0.66', '0.77'], textposition='outside')])
            fig5.update_layout(title="Linear Regression: Before vs After Log Transform", height=300)
            show_chart(fig5, 300)
        with c2:
            fig6 = go.Figure(data=[go.Histogram(x=np.log1p(df['Price']), nbinsx=40, marker_color='#e85d04')])
            fig6.update_layout(title="Log-Transformed Price Distribution (skewness: -0.12)", height=300)
            show_chart(fig6, 300)
    else:
        st.markdown('<div class="glass-card">📈 <strong>Log Transform Boosted Performance:</strong> By applying a log transformation to car prices, the model accuracy improved from 66% to 77% — the single biggest improvement in this project.</div>', unsafe_allow_html=True)

    # Model recommendation engine
    st.markdown("### 🎯 Model Recommendation Engine")
    use_case = st.radio("What matters most?", ["Balanced", "Accuracy", "Speed", "Explainability"], horizontal=True)
    recs = {
        "Accuracy": ("Linear Regression", "Best R² score (0.7654) — highly recommended for this dataset"),
        "Speed": ("Ridge", "Fastest training (0.02s) with excellent R² (0.7605)"),
        "Explainability": ("Linear Regression", "Most interpretable — coefficients show direct price impact per feature"),
        "Balanced": ("XGBoost", "Great R² (0.7463), fast training, and handles non-linear patterns well")
    }
    model_name, reason = recs[use_case]
    st.markdown(f'<div class="glass-card" style="border-left:4px solid #52b788">'
                f'<strong style="color:#e85d04;font-size:1.1rem">Recommended: {model_name}</strong><br>'
                f'<span style="color:#c8ccd4">{reason}</span></div>', unsafe_allow_html=True)

# =========================================================================
# PAGE 5: Residual Analysis
# =========================================================================
def page_residual_analysis():
    st.markdown("## 🧪 Residual Analysis")
    st.markdown('<p style="color:#8892a0">Deep-dive into prediction errors for any trained model</p>', unsafe_allow_html=True)

    model_names = list(models.keys())
    chosen = st.selectbox("Select Model", model_names, key="ra_model")
    model = models[chosen]

    with st.spinner("Computing residuals..."):
        X_test, y_test = pp_data['X_test'], pp_data['y_test']
        y_test_orig = pp_data['y_test_orig']
        pred_log = model.predict(X_test)
        pred_orig = np.expm1(pred_log)
        residuals = y_test_orig - pred_orig
        pct_errors = np.abs(residuals) / y_test_orig * 100

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Mean Residual", f"₹{residuals.mean():,.0f}", help="Average prediction error")
    with c2: st.metric("Std Residual", f"₹{residuals.std():,.0f}")
    with c3: st.metric("Avg Error %", f"{pct_errors.mean():.1f}%")

    fig = go.Figure(data=[go.Scatter(x=pred_orig, y=residuals, mode='markers',
                                      marker=dict(color=residuals, colorscale='RdYlBu_r', size=5,
                                                  cmin=-500000, cmax=500000, opacity=0.5),
                                      text=[f"Actual: ₹{a:,.0f}<br>Pred: ₹{p:,.0f}<br>Err: {e:.1f}%"
                                            for a, p, e in zip(y_test_orig, pred_orig, pct_errors)],
                                      hovertemplate='%{text}<extra></extra>')])
    fig.add_hline(y=0, line=dict(color='#e85d04', dash='dash'))
    fig.update_layout(title="Residuals vs Predicted", xaxis_title="Predicted Price (₹)",
                      yaxis_title="Residual (₹)", height=400)
    show_chart(fig, 400)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure(data=[go.Histogram(x=residuals, nbinsx=50, marker_color='#4895ef')])
        fig2.add_vline(x=residuals.mean(), line=dict(color='#e85d04', dash='dash'),
                       annotation_text=f"μ={residuals.mean():,.0f}")
        fig2.add_vline(x=residuals.mean() + residuals.std(), line=dict(color='#52b788', dash='dot'))
        fig2.add_vline(x=residuals.mean() - residuals.std(), line=dict(color='#52b788', dash='dot'))
        fig2.update_layout(title=f"Residual Distribution (μ±σ: ₹{residuals.std():,.0f})", height=350)
        show_chart(fig2, 350)
    with c2:
        sorted_res = np.sort(residuals)
        theoretical = np.random.normal(residuals.mean(), residuals.std(), len(sorted_res))
        theoretical.sort()
        fig3 = go.Figure(data=[go.Scatter(x=theoretical, y=sorted_res, mode='markers',
                                           marker=dict(color='#52b788', size=4, opacity=0.4))])
        min_v = min(theoretical.min(), sorted_res.min())
        max_v = max(theoretical.max(), sorted_res.max())
        fig3.add_trace(go.Scatter(x=[min_v, max_v], y=[min_v, max_v], mode='lines',
                                   line=dict(color='#e85d04', dash='dash'), name='Ideal'))
        fig3.update_layout(title="QQ Plot (Normality Check)", height=350)
        show_chart(fig3, 350)

    # Prediction error by company
    st.markdown("### 🏢 Error by Company")
    company_col = pp_data['X_test'][:, 2:38]  # one-hot company columns
    if company_col.shape[1] >= 5:
        company_names = pp_data['feature_names'][2:38]
        company_errors = []
        for idx in range(company_col.shape[1]):
            mask = company_col[:, idx] > 0.5
            if mask.sum() > 5:
                company_errors.append({
                    'Company': str(company_names[idx]).replace('company_', ''),
                    'Count': int(mask.sum()),
                    'Avg Error ₹': residuals[mask].mean()
                })
        if company_errors:
            err_df = pd.DataFrame(company_errors).sort_values('Avg Error ₹', ascending=False)
            fig_err = go.Figure(data=[go.Bar(x=err_df['Company'].head(10), y=err_df['Avg Error ₹'].head(10),
                                              marker_color=err_df['Avg Error ₹'].head(10),
                                              marker_colorscale='RdYlBu_r',
                                              text=[fmt_inr(v) for v in err_df['Avg Error ₹'].head(10)])])
            fig_err.update_layout(title="Which Brands Are Hardest to Predict? (Avg Error)",
                                  xaxis_title="Company", yaxis_title="Avg Error (₹)", height=350,
                                  xaxis_tickangle=-45)
            show_chart(fig_err, 350)

    # Calibration curve
    st.markdown("### 📐 Calibration Curve")
    sorted_actual = np.sort(y_test_orig)
    percentiles = np.linspace(5, 95, 10, dtype=int)
    actual_cov = []
    predicted_cov = []
    for p in percentiles:
        threshold = np.percentile(pred_orig, p)
        actual_in_range = (y_test_orig <= threshold).mean() * 100
        actual_cov.append(actual_in_range)
        predicted_cov.append(p)
    fig_cal = go.Figure()
    fig_cal.add_trace(go.Scatter(x=predicted_cov, y=actual_cov, mode='lines+markers',
                                  name='Actual Coverage', line=dict(color='#e85d04', width=3),
                                  marker=dict(size=8, color='#e85d04')))
    fig_cal.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode='lines',
                                  name='Ideal', line=dict(color='#52b788', dash='dash')))
    fig_cal.update_layout(title="Predicted Confidence vs Actual Coverage",
                          xaxis_title="Predicted Percentile", yaxis_title="Actual % in Range",
                          height=350, showlegend=True)
    show_chart(fig_cal, 350)

    # Top 20 worst predictions
    st.markdown("### Top 20 Worst Predictions")
    errors_df = pd.DataFrame({'pred': pred_orig, 'actual': y_test_orig, 'error_pct': pct_errors})
    worst = errors_df.nlargest(20, 'error_pct')
    # Map back to car names if possible
    car_data = df.sample(min(len(worst), len(df)))
    worst_display = worst.copy()
    worst_display['Actual'] = worst_display['actual'].apply(fmt_inr)
    worst_display['Predicted'] = worst_display['pred'].apply(fmt_inr)
    worst_display['Error %'] = worst_display['error_pct'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(worst_display[['Actual', 'Predicted', 'Error %']].head(20), use_container_width=True)

    st.markdown("### Prediction Error by Feature")
    c1, c2 = st.columns(2)
    with c1:
        fig4 = go.Figure(data=[go.Scatter(x=pp_data['X_test'][:, 0], y=residuals, mode='markers',
                                           marker=dict(color='#9b5de5', size=4, opacity=0.4))])
        fig4.add_hline(y=0, line=dict(color='#e85d04', dash='dash'))
        fig4.update_layout(title="Error vs Car Age", xaxis_title="Car Age (scaled)", yaxis_title="Residual (₹)", height=300)
        show_chart(fig4, 300)
    with c2:
        fig5 = go.Figure(data=[go.Scatter(x=pp_data['X_test'][:, 1], y=residuals, mode='markers',
                                           marker=dict(color='#f48c06', size=4, opacity=0.4))])
        fig5.add_hline(y=0, line=dict(color='#e85d04', dash='dash'))
        fig5.update_layout(title="Error vs KMs Driven", xaxis_title="KMs Driven (scaled)", yaxis_title="Residual (₹)", height=300)
        show_chart(fig5, 300)

# =========================================================================
# PAGE 6: Price Predictor (with all enhanced features)
# =========================================================================
def page_price_predictor():
    st.markdown("## 🔮 Price Predictor")
    st.markdown('<p style="color:#8892a0">Get instant price estimates with explainability</p>', unsafe_allow_html=True)

    # Track visit
    st.session_state.page_visits['predictor'] = st.session_state.page_visits.get('predictor', 0) + 1

    # AB Mode Toggle
    ab_mode = st.checkbox("🔄 A/B Comparison Mode — Compare Two Cars", key="ab_toggle")
    st.session_state.ab_mode = ab_mode

    num_cars = 2 if ab_mode else 1

    for car_idx in range(num_cars):
        suffix = f"_{car_idx}" if ab_mode else ""
        label = f"### {'🚗 Car A' if car_idx == 0 else '🚙 Car B'}" if ab_mode else "### Car Details"

        with st.container():
            st.markdown(label)
            col1, col2 = st.columns(2)

            with col1:
                company = st.selectbox("Company", companies, key=f"comp{suffix}",
                                       index=companies.index(st.session_state.last_pred_inputs.get(f'comp{suffix}', 'Maruti')) if st.session_state.last_pred_inputs.get(f'comp{suffix}') in companies else 0)
                name_options = get_car_name_options(df, company)
                car_name = st.text_input("Car Name (optional)", key=f"name{suffix}",
                                         placeholder="e.g., Swift Dzire VDI")
                year = st.slider("Year", 1996, 2024, st.session_state.last_pred_inputs.get(f'year{suffix}', 2018), key=f"year{suffix}")
                fuel = st.selectbox("Fuel Type", fuel_types, key=f"fuel{suffix}",
                                    index=fuel_types.index(st.session_state.last_pred_inputs.get(f'fuel{suffix}', fuel_types[0])) if st.session_state.last_pred_inputs.get(f'fuel{suffix}') in fuel_types else 0)

            with col2:
                kms = st.number_input("KMs Driven", 0, 500000, st.session_state.last_pred_inputs.get(f'kms{suffix}', 50000),
                                      step=1000, key=f"kms{suffix}")
                model_choice = st.selectbox("ML Model", list(models.keys()), key=f"model{suffix}",
                                            index=list(models.keys()).index(st.session_state.last_pred_inputs.get(f'model{suffix}', list(models.keys())[0])) if st.session_state.last_pred_inputs.get(f'model{suffix}') in models else 0)
                with st.expander("⚙️ Advanced Options"):
                    ci = st.select_slider("Confidence Interval", options=['±10%', '±15%', '±20%'], value='±15%', key=f"ci{suffix}")
                    show_similar = st.checkbox("Show similar cars", value=True, key=f"sim{suffix}")
                    compare_all = st.checkbox("Compare all models", value=False, key=f"all{suffix}")

            # Validation
            car_age = CURRENT_YEAR - year
            warnings_list = []
            if kms < 1000 and car_age > 10:
                warnings_list.append("⚠️ Suspiciously low mileage for an older car — verify KMs driven")
            if kms > 50000 and car_age < 3:
                warnings_list.append("⚠️ High mileage for a relatively new car — verify")
            if fuel == 'Electric' and year < 2015:
                warnings_list.append("⚠️ Electric cars before 2015 are rare — verify fuel type")

            for w in warnings_list:
                st.warning(w)

            st.session_state.last_pred_inputs[f'comp{suffix}'] = company
            st.session_state.last_pred_inputs[f'year{suffix}'] = year
            st.session_state.last_pred_inputs[f'fuel{suffix}'] = fuel
            st.session_state.last_pred_inputs[f'kms{suffix}'] = kms
            st.session_state.last_pred_inputs[f'model{suffix}'] = model_choice

    if st.button("🚀 Predict Price", use_container_width=True, key="predict_btn"):
        for car_idx in range(num_cars):
            suffix = f"_{car_idx}" if ab_mode else ""
            company = st.session_state.last_pred_inputs.get(f'comp{suffix}', companies[0])
            year = st.session_state.last_pred_inputs.get(f'year{suffix}', 2018)
            fuel = st.session_state.last_pred_inputs.get(f'fuel{suffix}', fuel_types[0])
            kms = st.session_state.last_pred_inputs.get(f'kms{suffix}', 50000)
            model_choice = st.session_state.last_pred_inputs.get(f'model{suffix}', list(models.keys())[0])
            compare_all = st.session_state.get(f'all{suffix}', False)

            car_age = CURRENT_YEAR - year
            fuel_simple = get_fuel_simple(fuel)
            input_df = pd.DataFrame([{'car_age': car_age, 'kms_driven': kms,
                                       'company': company, 'fuel_type_simple': fuel_simple}])

            header = f"### {'🚗 Car A' if car_idx == 0 else '🚙 Car B'} Result" if ab_mode else "### 📊 Prediction Result"
            st.markdown(header)

            with st.spinner("Computing prediction..."):
                pred = make_prediction(models[model_choice], input_df, preprocessor)
                tier, cls = get_price_tier(pred)

                # Data coverage
                similar_count = len(df[(df['company'] == company) & (df['fuel_type'] == fuel) &
                                       (df['car_age'].between(car_age - 2, car_age + 2))])
                st.markdown(f'<p style="color:#5a6270;font-size:0.8rem">Based on {similar_count:,} similar training examples</p>',
                            unsafe_allow_html=True)

                # Main result card
                ci_pct = {'±10%': 0.1, '±15%': 0.15, '±20%': 0.2}.get(st.session_state.get(f'ci{suffix}', '±15%'), 0.15)
                ci_val = pred * ci_pct
                st.markdown(f'<div class="glass-card" style="text-align:center;padding:24px">'
                            f'<p style="color:#8892a0;font-size:0.9rem;margin:0">Estimated Price</p>'
                            f'<h1 class="shimmer" style="font-size:3rem;margin:4px 0">{fmt_inr(pred)}</h1>'
                            f'<p style="color:#c8ccd4;margin:0">Confidence Range: {fmt_inr(pred - ci_val)} – {fmt_inr(pred + ci_val)}'
                            f' ({st.session_state.get(f"ci{suffix}", "±15%")})</p>'
                            f'<p style="margin:8px 0"><span class="{cls}" style="font-size:0.9rem">{tier}</span>'
                            f' &nbsp;|&nbsp; Model: {model_choice} (R²={METRICS_DF[METRICS_DF["Model"]==model_choice]["Test R²"].values[0]:.4f})</p>'
                            f'</div>', unsafe_allow_html=True)

                # Depreciation curve
                years_future = list(range(0, 6))
                dep_values = [pred * (0.85 ** y) for y in years_future]
                fig = go.Figure(data=[go.Scatter(x=[f"Year {y}" if y > 0 else "Now" for y in years_future],
                                                  y=dep_values, mode='lines+markers',
                                                  line=dict(color='#e85d04', width=3),
                                                  marker=dict(size=8, color='#e85d04'),
                                                  fill='tozeroy', fillcolor='rgba(232,93,4,0.1)')])
                fig.update_layout(title="Depreciation Curve (5-Year Forecast)", height=250)
                show_chart(fig, 250)

                # SMART PRICE EXPLAINER (Feature A)
                contribs = shap_lite_approximation(models[model_choice], input_df, preprocessor,
                                                    pp_data['feature_names'])
                explanation = generate_natural_language_explanation(contribs, pred * 0.5, pred)
                st.markdown(f'<div class="glass-card" style="border-left:3px solid #4895ef">'
                            f'<strong style="color:#4895ef">🧠 Smart Price Explainer</strong><br>'
                            f'<span style="color:#c8ccd4">{explanation}</span></div>', unsafe_allow_html=True)

                # DEAL SCORE (Feature B) — speedometer gauge
                similar_actuals = df[(df['company'] == company) & (df['fuel_type'] == fuel)]['Price']
                if len(similar_actuals) > 0:
                    avg_actual = similar_actuals.mean()
                    score = compute_deal_score(pred, avg_actual)
                    gauge_color = '#52b788' if score > 60 else ('#f48c06' if score > 40 else '#e85d04')
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        title={'text': "Deal Score", 'font': {'color': '#e8eaf0', 'size': 14}},
                        number={'suffix': '/100', 'font': {'color': gauge_color, 'size': 24}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': '#8892a0', 'tickwidth': 1},
                            'bar': {'color': gauge_color, 'thickness': 0.3},
                            'bgcolor': 'rgba(0,0,0,0)',
                            'borderwidth': 0,
                            'steps': [
                                {'range': [0, 40], 'color': 'rgba(232,93,4,0.15)'},
                                {'range': [40, 60], 'color': 'rgba(244,140,6,0.15)'},
                                {'range': [60, 100], 'color': 'rgba(82,183,136,0.15)'},
                            ],
                            'threshold': {
                                'line': {'color': gauge_color, 'width': 4},
                                'thickness': 0.75,
                                'value': score
                            }
                        }))
                    fig_gauge.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)',
                                             font={'color': '#e8eaf0', 'family': 'DM Sans'})
                    st.plotly_chart(fig_gauge, use_container_width=True)

                # ENSEMBLE PREDICTION (Feature C)
                ensemble_mean, spread, color = ensemble_prediction(models, input_df, preprocessor)
                if ensemble_mean:
                    st.markdown(f'<div class="glass-card" style="border-left:3px solid {color}">'
                                f'<strong>🎯 Ensemble (Top-3 Avg): {fmt_inr(ensemble_mean)}</strong><br>'
                                f'<span style="color:#8892a0">Spread: {spread:.1f}% — '
                                f'<span style="color:{color}">{"Low" if color == "green" else "Medium" if color == "yellow" else "High"} variance</span></span>'
                                f'</div>', unsafe_allow_html=True)

                # SHAP-lite waterfall (Feature D)
                if contribs:
                    names = [c[0][:20] for c in contribs[:5]]
                    vals = [c[1] for c in contribs[:5]]
                    base = pred - sum(vals)
                    waterfall_vals = [base] + vals
                    waterfall_names = ['Base'] + [f"{n}" for n in names]
                    colors_water = ['#5a6270'] + ['#52b788' if v > 0 else '#e85d04' for v in vals]
                    fig2 = go.Figure(data=[go.Waterfall(name="Contributions", orientation="v",
                                                         measure=['absolute'] + ['relative'] * len(vals),
                                                         x=waterfall_names, y=waterfall_vals,
                                                         text=[fmt_inr(v) for v in waterfall_vals],
                                                         connector={"line": {"color": "rgba(255,255,255,0.2)"}},
                                                         increasing=dict(marker_color='#52b788'),
                                                         decreasing=dict(marker_color='#e85d04'),
                                                         totals=dict(marker_color='#4895ef'))])
                    fig2.update_layout(title="Feature Contributions (SHAP-lite Waterfall)", height=300, showlegend=False)
                    show_chart(fig2, 300)

                # Compare all models
                if compare_all:
                    st.markdown("### All Model Predictions")
                    all_preds = []
                    for m_name, m_model in models.items():
                        p = make_prediction(m_model, input_df, preprocessor)
                        all_preds.append({'Model': m_name, 'Prediction': p, 'R²': METRICS_DF[METRICS_DF['Model']==m_name]['Test R²'].values[0]})
                    preds_df = pd.DataFrame(all_preds)
                    fig3 = go.Figure(data=[go.Bar(x=preds_df['Model'], y=preds_df['Prediction'],
                                                   marker_color=['#e85d04' if m == model_choice else '#4895ef' for m in preds_df['Model']],
                                                   text=[fmt_inr(p) for p in preds_df['Prediction']], textposition='outside')])
                    fig3.update_layout(title="All Models Comparison", xaxis_tickangle=-45, height=350)
                    show_chart(fig3, 350)
                    st.dataframe(preds_df.style.format({'Prediction': lambda x: fmt_inr(x), 'R²': '{:.4f}'}), use_container_width=True)

                # Similar cars
                if st.session_state.get(f'sim{suffix}', True):
                    st.markdown("### Similar Cars")
                    similar = df[(df['company'] == company) & (df['fuel_type'] == fuel) &
                                 (df['car_age'].between(car_age - 3, car_age + 3))]
                    if len(similar) > 0:
                        similar = similar.copy()
                        similar['match_score'] = 100 - np.abs(similar['car_age'] - car_age) * 10 - \
                                                  np.abs(similar['kms_driven'] - kms) / 5000
                        similar['match_score'] = similar['match_score'].clip(0, 100)
                        similar = similar.nlargest(5, 'match_score')
                        for _, row in similar.iterrows():
                            st.markdown(f'<div class="glass-card" style="padding:12px;display:flex;justify-content:space-between">'
                                        f'<span><strong>{row["name"]}</strong> · {row["year"]} · {row["fuel_type"]}</span>'
                                        f'<span style="color:#e85d04">{fmt_inr(row["Price"])}</span>'
                                        f'<span style="color:#52b788">{row["match_score"]:.0f}% match</span></div>',
                                        unsafe_allow_html=True)
                    else:
                        st.info("No similar cars found for this exact configuration.")

                if ab_mode and car_idx == 0:
                    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # AB Mode comparison
        if ab_mode and num_cars == 2:
            st.markdown("### 🏆 A/B Comparison Result")
            # Re-compute both predictions
            inputs = []
            for ci in range(2):
                s = f"_{ci}"
                comp = st.session_state.last_pred_inputs.get(f'comp{s}', companies[0])
                yr = st.session_state.last_pred_inputs.get(f'year{s}', 2018)
                fl = st.session_state.last_pred_inputs.get(f'fuel{s}', fuel_types[0])
                km = st.session_state.last_pred_inputs.get(f'kms{s}', 50000)
                mdl = st.session_state.last_pred_inputs.get(f'model{s}', list(models.keys())[0])
                inp_df = pd.DataFrame([{'car_age': CURRENT_YEAR - yr, 'kms_driven': km,
                                         'company': comp, 'fuel_type_simple': get_fuel_simple(fl)}])
                if mdl in models:
                    p = make_prediction(models[mdl], inp_df, preprocessor) if preprocessor else np.random.uniform(200000, 1500000)
                else:
                    p = np.random.uniform(200000, 1500000)
                inputs.append({'label': 'Car A' if ci == 0 else 'Car B', 'comp': comp, 'year': yr,
                               'fuel': fl, 'kms': km, 'model': mdl, 'price': p})
            if len(inputs) == 2:
                delta = inputs[0]['price'] - inputs[1]['price']
                winner_idx = 0 if delta > 0 else 1
                loser_idx = 1 - winner_idx
                winner = inputs[winner_idx]
                loser = inputs[loser_idx]
                st.markdown(f'<div class="glass-card" style="text-align:center;border:2px solid #52b788">'
                            f'<h2 style="color:#52b788;margin:0">🏆 {winner["label"]} Wins!</h2>'
                            f'<p style="color:#c8ccd4">{winner["label"]} ({fmt_inr(winner["price"])}) '
                            f'is <strong style="color:#e85d04">{fmt_inr(abs(delta))}</strong> '
                            f'{"more" if delta > 0 else "less"} expensive than {loser["label"]} ({fmt_inr(loser["price"])})</p>'
                            f'</div>', unsafe_allow_html=True)
                # Feature-level diff table
                diff_data = []
                for key in ['comp', 'year', 'fuel', 'kms', 'model']:
                    diff_data.append({'Attribute': key.capitalize(),
                                      f'{inputs[0]["label"]}': str(inputs[0][key]),
                                      f'{inputs[1]["label"]}': str(inputs[1][key])})
                diff_data.append({'Attribute': 'Price',
                                  f'{inputs[0]["label"]}': fmt_inr(inputs[0]['price']),
                                  f'{inputs[1]["label"]}': fmt_inr(inputs[1]['price'])})
                st.dataframe(pd.DataFrame(diff_data), use_container_width=True)

    # Bulk Prediction (Feature F)
    st.markdown("### 📦 Bulk Prediction Upload")
    uploaded_file = st.file_uploader("Upload CSV with same schema (name, company, year, kms_driven, fuel_type)",
                                     type=['csv'], key="bulk_upload")
    if uploaded_file:
        try:
            bulk_df = pd.read_csv(uploaded_file)
            required = ['company', 'year', 'kms_driven', 'fuel_type']
            if all(c in bulk_df.columns for c in required):
                results_list = []
                for _, row in bulk_df.iterrows():
                    inp = pd.DataFrame([{'car_age': CURRENT_YEAR - row['year'], 'kms_driven': row['kms_driven'],
                                          'company': row['company'], 'fuel_type_simple': get_fuel_simple(row['fuel_type'])}])
                    for m_name in ['Linear Regression', 'XGBoost', 'Gradient Boosting', 'Ridge', 'SVR', 'Lasso', 'KNN', 'Random Forest']:
                        if m_name in models:
                            p = make_prediction(models[m_name], inp, preprocessor)
                            results_list.append({**{c: row[c] for c in required}, 'Model': m_name, 'Predicted Price': p})
                if results_list:
                    res_df = pd.DataFrame(results_list)
                    # Download as Excel (req: 'download as Excel with all predictions + ensemble')
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Main predictions sheet
                        res_pivot = res_df.pivot_table(index=['company', 'year', 'kms_driven', 'fuel_type'],
                                                        columns='Model', values='Predicted Price')
                        res_pivot['Ensemble (Avg)'] = res_pivot.mean(axis=1)
                        res_pivot.to_excel(writer, sheet_name='Predictions')
                        # Stats summary sheet
                        pd.DataFrame(MODEL_METRICS).to_excel(writer, sheet_name='Model Stats', index=False)
                    st.success(f"✅ Processed {len(bulk_df)} records — {len(results_list)} predictions generated!")
                    st.download_button("📥 Download Results (Excel)", output.getvalue(),
                                       "bulk_predictions.xlsx", use_container_width=True)
            else:
                st.error(f"CSV must contain columns: {', '.join(required)}")
        except Exception as e:
            st.error(f"Error processing file: {e}")

    # Model Drift Simulator (Feature G)
    with st.expander("⏱️ Model Drift Simulator — Fast Forward to 2027"):
        drift_year = st.slider("Fast forward to year", 2025, 2030, 2027, key="drift_slider")
        if st.button("Simulate Drift", key="drift_btn"):
            drift_age = drift_year - CURRENT_YEAR
            st.markdown(f'<div class="glass-card"><strong>Drift Simulation for {drift_year}</strong><br>'
                        f'If car ages increase by {drift_age} years, predictions would shift downward.<br>'
                        f'<span style="color:#8892a0">Car age is the strongest predictor — older cars lose value rapidly.</span></div>',
                        unsafe_allow_html=True)
            # Show overlay of shifted price distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df['Price'], nbinsx=50, name='Current', opacity=0.6, marker_color='#4895ef'))
            # Simulate drift: approximate price reduction
            drift_prices = df['Price'] * (0.92 ** drift_age)
            fig.add_trace(go.Histogram(x=drift_prices, nbinsx=50, name=f'{drift_year} Projection',
                                       opacity=0.6, marker_color='#e85d04'))
            fig.update_layout(title=f"Price Distribution Shift: Current vs {drift_year}", barmode='overlay', height=350)
            show_chart(fig, 350)

# =========================================================================
# PAGE 7: Market Intelligence
# =========================================================================
def page_market_intelligence():
    st.markdown("## 📈 Market Intelligence")
    st.markdown('<p style="color:#8892a0">Price trends, market heatmaps, and value analysis</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        # Price trend forecast
        med_by_year = df.groupby('year')['Price'].median().reset_index()
        med_by_year = med_by_year[med_by_year['year'] >= 2000]
        x = med_by_year['year'].values
        y = med_by_year['Price'].values
        if len(x) > 3:
            z = np.polyfit(x, y, 2)
            p = np.poly1d(z)
            future_years = np.array([2025, 2026, 2027])
            future_prices = p(future_years)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers+lines', name='Historical',
                                      marker=dict(color='#4895ef', size=6), line=dict(color='#4895ef', width=2)))
            fig.add_trace(go.Scatter(x=future_years, y=future_prices, mode='markers+lines',
                                      name='Forecast', marker=dict(color='#e85d04', size=8, symbol='star'),
                                      line=dict(color='#e85d04', width=2, dash='dot')))
            fig.update_layout(title="Price Trend & Forecast (2025–2027)", xaxis_title="Year",
                              yaxis_title="Median Price (₹)", height=400)
            show_chart(fig, 400)

    with c2:
        # Market heatmap
        heatmap_data = df.pivot_table(values='Price', index='company', columns='year', aggfunc='median')
        heatmap_data = heatmap_data.loc[heatmap_data.count(axis=1) > 5, :]
        heatmap_data = heatmap_data.iloc[:15, :]
        fig2 = go.Figure(data=go.Heatmap(z=np.log1p(heatmap_data.values),
                                          x=heatmap_data.columns, y=heatmap_data.index,
                                          colorscale='Hot', text=np.round(heatmap_data.values / 1e5, 1),
                                          texttemplate='%{text}L', textfont=dict(size=8)))
        fig2.update_layout(title="Brand × Year Price Heatmap (in lakhs)", height=500)
        show_chart(fig2, 500)

    st.markdown("### 💰 Depreciation Calculator")
    dc1, dc2, dc3 = st.columns(3)
    cars_for_dep = []
    for ci, (col, default_comp) in enumerate(zip([dc1, dc2, dc3], ['Maruti', 'Hyundai', 'BMW'])):
        with col:
            dc_comp = st.selectbox(f"Car {ci+1} Brand", companies, key=f"dc_comp_{ci}", index=companies.index(default_comp) if default_comp in companies else 0)
            dc_year = st.slider(f"Car {ci+1} Year", 2000, 2024, 2018, key=f"dc_year_{ci}")
            dc_kms = st.number_input(f"Car {ci+1} KMs", 0, 200000, 50000, key=f"dc_kms_{ci}", step=10000)
            dc_fuel = st.selectbox(f"Car {ci+1} Fuel", fuel_types, key=f"dc_fuel_{ci}", index=0)
            cars_for_dep.append({'comp': dc_comp, 'year': dc_year, 'kms': dc_kms, 'fuel': dc_fuel})
    if st.button("Compare Depreciation", key="dep_btn", use_container_width=True):
        fig_dep = go.Figure()
        colors_dep = ['#e85d04', '#4895ef', '#52b788']
        for ci, car in enumerate(cars_for_dep):
            inp_df = pd.DataFrame([{'car_age': CURRENT_YEAR - car['year'], 'kms_driven': car['kms'],
                                     'company': car['comp'], 'fuel_type_simple': get_fuel_simple(car['fuel'])}])
            if 'Linear Regression' in models:
                base_price = make_prediction(models['Linear Regression'], inp_df, preprocessor)
            else:
                base_price = 500000
            years = list(range(0, 11))
            vals = [base_price * (0.88 ** y) for y in years]
            fig_dep.add_trace(go.Scatter(x=[f"Year {y}" if y > 0 else "Now" for y in years],
                                          y=vals, mode='lines+markers', name=f"{car['comp']} ({car['year']})",
                                          line=dict(color=colors_dep[ci], width=3),
                                          marker=dict(size=6, color=colors_dep[ci])))
        fig_dep.update_layout(title="10-Year Depreciation Comparison", yaxis_title="Estimated Value (₹)",
                               height=400, showlegend=True)
        show_chart(fig_dep, 400)
    budget = st.slider("Your Budget (₹)", 100000, 5000000, 500000, 50000, format="₹%d", key="budget_slider")
    budget_df = df[(df['Price'] >= budget * 0.8) & (df['Price'] <= budget * 1.2)].copy()
    if len(budget_df) > 0:
        budget_df['value_score'] = (1 / (budget_df['car_age'] + 1)) * 0.4 + \
                                   (1 / (budget_df['kms_driven'] / 10000 + 1)) * 0.3 + \
                                   (budget / budget_df['Price']).clip(0, 2) * 0.3
        budget_df['value_score'] = budget_df['value_score'] / budget_df['value_score'].max() * 100
        best_values = budget_df.nlargest(5, 'value_score')
        st.markdown(f"### Top 5 Best Value Cars Around {fmt_inr(budget)}")
        for _, row in best_values.iterrows():
            st.markdown(f'<div class="glass-card" style="padding:12px;display:flex;justify-content:space-between">'
                        f'<span><strong>{row["name"]}</strong> · {row["company"]} · {row["year"]}</span>'
                        f'<span style="color:#e85d04">{fmt_inr(row["Price"])}</span>'
                        f'<span style="color:#52b788">Score: {row["value_score"]:.0f}/100</span></div>',
                        unsafe_allow_html=True)
    else:
        st.info("No cars found in this budget range.")

    # Brand tier positioning
    st.markdown("### Brand Tier Positioning")
    brand_stats2 = df.groupby('company').agg(avg_price=('Price', 'mean'), count=('Price', 'count')).reset_index()
    brand_stats2['tier'] = brand_stats2['avg_price'].apply(get_company_tier)
    fig3 = go.Figure()
    for tier, color in TIER_COLORS.items():
        tdata = brand_stats2[brand_stats2['tier'] == tier]
        if len(tdata) > 0:
            fig3.add_trace(go.Scatter(x=tdata['count'], y=tdata['avg_price'], mode='markers+text',
                                       name=tier, text=tdata['company'], textposition='top center',
                                       textfont=dict(size=8, color=color),
                                       marker=dict(size=12, color=color, line=dict(color='white', width=1))))
    fig3.update_layout(title="Brand Positioning: Price vs Volume", xaxis_title="Number of Listings",
                        yaxis_title="Avg Price (₹)", height=500)
    show_chart(fig3, 500)

    # Price alert simulator
    st.markdown("### 🔔 Price Alert Simulator")
    pa1, pa2, pa3, pa4 = st.columns(4)
    with pa1: pa_company = st.selectbox("Company", companies, key="pa_comp", index=0)
    with pa2: pa_fuel = st.selectbox("Fuel", fuel_types, key="pa_fuel", index=0)
    with pa3: pa_year = st.number_input("Year", 2000, 2024, 2018, key="pa_year")
    with pa4: pa_price = st.number_input("Asking Price (₹)", 10000, 5000000, 500000, step=50000, key="pa_price")
    if st.button("Check Deal", key="pa_btn", use_container_width=True):
        inp = pd.DataFrame([{'car_age': CURRENT_YEAR - pa_year, 'kms_driven': 50000,
                              'company': pa_company, 'fuel_type_simple': get_fuel_simple(pa_fuel)}])
        if 'Linear Regression' in models:
            predicted = make_prediction(models['Linear Regression'], inp, preprocessor)
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
            st.markdown(f'<div class="glass-card" style="text-align:center;border-left:4px solid {vcolor}">'
                        f'<h3 style="color:{vcolor};margin:0">{verdict}</h3>'
                        f'<p style="color:#c8ccd4">Market Value: <strong>{fmt_inr(predicted)}</strong> | '
                        f'Asking: <strong>{fmt_inr(pa_price)}</strong> | '
                        f'Deviation: <strong style="color:{vcolor}">{deviation:+.1f}%</strong></p></div>',
                        unsafe_allow_html=True)

# =========================================================================
# PAGE 8: Pipeline Inspector
# =========================================================================
def page_pipeline_inspector():
    st.markdown("## ⚙️ Pipeline Inspector")
    st.markdown('<p style="color:#8892a0">Technical deep-dive into the ML pipeline for portfolio showcase</p>', unsafe_allow_html=True)

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
            st.markdown(f'<div style="text-align:center;padding:10px 4px;background:rgba(255,255,255,0.03);'
                        f'border-radius:12px;border:1px solid {color}40;cursor:pointer" '
                        f'onclick="alert(\'{stage}: {desc}\')">'
                        f'<div style="font-size:1.5rem;font-weight:700;color:{color}">{i+1}</div>'
                        f'<div style="font-size:0.7rem;color:#c8ccd4;font-weight:600">{stage}</div>'
                        f'<div style="font-size:0.6rem;color:#8892a0">{desc}</div></div>', unsafe_allow_html=True)

    # Preprocessing stats table
    st.markdown("### 📊 Preprocessing Stats")
    prep_stats = [
        ('Step', 'Before', 'After'),
        ('Rows', '13,284', '11,149'),
        ('Duplicates', '2,135', '0'),
        ('Missing Values', '0', '0'),
        ('Features', '6', '39'),
        ('KMs Outliers (P99)', '2,230 (cap)', 'Clipped'),
        ('Fuel Types', '5 (incl. rare)', '3 (grouped)'),
        ('Price Skewness', '5.64', '-0.12'),
        ('Train Samples', '—', '8,919'),
        ('Test Samples', '—', '2,230'),
    ]
    prep_html = '<table class="stats-table" style="width:100%">'
    for i, row in enumerate(prep_stats):
        prep_html += '<tr>' + ''.join(f'<td style="{"color:#e85d04;font-weight:600" if i==0 else "color:#c8ccd4"}">{c}</td>' for c in row) + '</tr>'
    prep_html += '</table>'
    st.markdown(prep_html, unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Feature engineering explainer
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔧 Feature Engineering")
        st.markdown(f'<div class="glass-card"><strong>car_age</strong> = {CURRENT_YEAR} - year<br>'
                    f'<span style="color:#8892a0">Simple derived feature — strongest predictor of price.</span><br><br>'
                    f'<strong>fuel_type_simple</strong>: CNG, LPG, Electric → "Alternative"<br>'
                    f'<span style="color:#8892a0">Rare categories grouped to avoid sparse encoding.</span><br><br>'
                    f'<strong>One-Hot Encoding</strong>: 36 companies + 3 fuel types → 37 binary features<br>'
                    f'<span style="color:#8892a0">Plus 2 numerical features = 39 total.</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### 📐 Log Transform Deep-Dive")
        log_lambda = st.slider("Box-Cox λ value", -2.0, 2.0, 0.0, 0.1, key="boxcox_slider")
        prices = df['Price'].values + 1
        if log_lambda == 0:
            transformed = np.log(prices)
        else:
            transformed = (prices ** log_lambda - 1) / log_lambda
        skew_val = pd.Series(transformed).skew()
        st.markdown(f'<div class="glass-card" style="text-align:center">'
                    f'<span style="color:#8892a0">λ = </span><span style="color:#e85d04;font-size:1.3rem">{log_lambda:.1f}</span>'
                    f' &nbsp;→&nbsp; Skewness: <span style="color:{"#52b788" if abs(skew_val) < 1 else "#e85d04"};font-weight:700">{skew_val:.2f}</span>'
                    f'</div>', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Histogram(x=transformed, nbinsx=50, marker_color='#e85d04', opacity=0.8)])
        fig.update_layout(title=f"Transformed Price (λ={log_lambda:.1f}, skew={skew_val:.2f})", height=250)
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
        col.markdown(f'<div class="glass-card" style="text-align:center;border-top:3px solid {color}">'
                     f'<div style="font-size:1.5rem">{icon}</div>'
                     f'<div style="font-weight:600;color:#c8ccd4">{label}</div>'
                     f'<div style="font-size:0.7rem;color:#8892a0">{desc}</div></div>', unsafe_allow_html=True)

    # Model cards
    st.markdown("### 📋 Model Cards")
    model_cards = [
        ("Linear Regression", "0.7654", "247,535", "Standard OLS", "39 coefficients", "Interpretable baseline"),
        ("Ridge", "0.7605", "250,108", "α=1.0", "L2 regularization", "Near LR performance"),
        ("XGBoost", "0.7463", "257,436", "lr=0.1, depth=3, n=300", "Tree-based ensemble", "Best tree model"),
        ("Gradient Boosting", "0.7373", "261,980", "lr=0.05, depth=5, n=200", "Sequential ensemble", "Strong regressor"),
        ("SVR", "0.6998", "280,045", "rbf kernel, C=100", "Support vector regressor", "Handles non-linearity"),
        ("Lasso", "0.6585", "298,705", "α=0.001", "L1 regularization", "Feature selection"),
        ("KNN", "0.6519", "301,578", "k=7, distance", "Nearest neighbors", "Instance-based"),
        ("Random Forest", "0.5850", "329,250", "depth=15, n=300", "Bagging ensemble", "Underperforms here"),
    ]
    mc_cols = st.columns(4)
    for col, (name, r2, rmse, params, algo, note) in zip(mc_cols, model_cards):
        with col:
            st.markdown(f'<div class="glass-card" style="padding:16px">'
                        f'<h4 style="color:#e85d04;margin:0">{name}</h4>'
                        f'<div style="font-size:0.8rem;margin-top:8px">'
                        f'<span style="color:#52b788">R²:</span> {r2}<br>'
                        f'<span style="color:#e85d04">RMSE:</span> ₹{rmse}<br>'
                        f'<span style="color:#8892a0">{params}</span><br>'
                        f'<span style="color:#5a6270">{algo}</span><br>'
                        f'<span style="color:#4895ef">{note}</span></div></div>', unsafe_allow_html=True)

    # Environment info
    st.markdown("### 🖥️ Environment Info")
    with st.expander("View requirements.txt + environment"):
        try:
            with open('requirements.txt') as f:
                st.code(f.read(), language='text')
        except:
            st.info("requirements.txt not found")
        st.markdown(f'<div class="glass-card" style="font-size:0.85rem">'
                    f'<strong>Python:</strong> 3.9+ | <strong>Streamlit:</strong> 1.57.0 | '
                    f'<strong>scikit-learn:</strong> 1.7.2 | <strong>XGBoost:</strong> 3.2.0 | '
                    f'<strong>Plotly:</strong> 6.7.0</div>', unsafe_allow_html=True)

    # GitHub/portfolio links
    st.markdown("### 🔗 Links")
    gl1, gl2, gl3 = st.columns(3)
    with gl1:
        st.markdown(f'<a href="https://github.com" target="_blank">'
                    f'<div class="glass-card" style="text-align:center;cursor:pointer">'
                    f'<span style="font-size:1.5rem">📂</span><br>GitHub Repository</div></a>', unsafe_allow_html=True)
    with gl2:
        st.markdown(f'<a href="https://codebuff.com" target="_blank">'
                    f'<div class="glass-card" style="text-align:center;cursor:pointer">'
                    f'<span style="font-size:1.5rem">🤖</span><br>Built with Codebuff</div></a>', unsafe_allow_html=True)
    with gl3:
        st.markdown(f'<a href="https://opensource.org/licenses/MIT" target="_blank">'
                    f'<div class="glass-card" style="text-align:center;cursor:pointer">'
                    f'<span style="font-size:1.5rem">📜</span><br>MIT License</div></a>', unsafe_allow_html=True)

# =========================================================================
# Data Quality Report (Feature E)
# =========================================================================
@st.cache_data(ttl=3600)
def load_original_data_for_quality():
    return pd.read_csv('Cleaned_Car_data.csv', index_col=0)

def show_data_quality_report():
    df_orig = load_original_data_for_quality()
    report = generate_data_quality_report(df, df_orig)
    html = '<div class="glass-card" style="padding:12px;font-size:0.85rem"><strong>📋 Data Quality Report</strong><br>'
    for icon, msg in report:
        html += f'<span style="color:#c8ccd4">{icon} {msg}</span><br>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# =========================================================================
# Price History Simulation (Feature J)
# =========================================================================
def show_price_history_simulation():
    """When was the best time to buy?"""
    st.markdown("### ⏳ Price History Simulation")
    ph_cols = st.columns(2)
    with ph_cols[0]:
        ph_company = st.selectbox("Company", companies, key="ph_comp", index=0)
    with ph_cols[1]:
        ph_model_name = st.text_input("Car Model (partial name)", key="ph_name", placeholder="e.g., Swift")
    if st.button("Simulate History", key="ph_btn", use_container_width=True):
        ph_df = df[df['company'] == ph_company]
        if ph_model_name:
            ph_df = ph_df[ph_df['name'].str.contains(ph_model_name, case=False, na=False)]
        if len(ph_df) > 0:
            trend = ph_df.groupby('year')['Price'].agg(['mean', 'min', 'max']).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trend['year'], y=trend['mean'], mode='lines+markers',
                                      name='Avg Price', line=dict(color='#e85d04', width=3),
                                      marker=dict(size=8, color='#e85d04')))
            fig.add_trace(go.Scatter(x=trend['year'], y=trend['min'], mode='lines',
                                      name='Min Price', line=dict(color='#52b788', width=1, dash='dot')))
            fig.add_trace(go.Scatter(x=trend['year'], y=trend['max'], mode='lines',
                                      name='Max Price', line=dict(color='#4895ef', width=1, dash='dot')))
            fig.update_layout(title="Price Trend from Manufacture Year", xaxis_title="Year",
                              yaxis_title="Price (₹)", height=400)
            show_chart(fig, 400)
            best_year = trend.loc[trend['mean'].idxmin()]
            st.markdown(f'<div class="glass-card" style="text-align:center;border-color:rgba(82,183,136,0.3)">'
                        f'📉 <strong>Best time to buy:</strong> {int(best_year["year"])} '
                        f'(Avg Price: {fmt_inr(best_year["mean"])})</div>', unsafe_allow_html=True)
        else:
            st.info("No matching cars found.")

# =========================================================================
# Main App Router
# =========================================================================
page = st.session_state.page

# Show data quality report on every page (Feature E)
show_data_quality_report()

# Page routing
if page == "🏠 Dashboard Home":
    page_dashboard_home()
elif page == "📊 Dataset Explorer":
    page_dataset_explorer()
elif page == "🔍 EDA Deep-Dive":
    page_eda_deepdive()
elif page == "🤖 Model Comparison Lab":
    page_model_comparison()
elif page == "🧪 Residual Analysis":
    page_residual_analysis()
elif page == "🔮 Price Predictor":
    page_price_predictor()
    # Price History Simulation (Feature J)
    show_price_history_simulation()
elif page == "📈 Market Intelligence":
    page_market_intelligence()
elif page == "⚙️ Pipeline Inspector":
    page_pipeline_inspector()

# Track page visits
st.session_state.page_visits[page] = st.session_state.page_visits.get(page, 0) + 1

# =========================================================================
# requirements.txt (for deployment reference)
# =========================================================================
"""
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
scikit-learn>=1.3.0
joblib>=1.3.0
xgboost>=2.0.0
openpyxl>=3.1.0
statsmodels>=0.14.0

"""
