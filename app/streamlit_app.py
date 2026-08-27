"""
AutoIntel — Used Car Price Intelligence
=========================================
Production-ready Streamlit dashboard for the Car Price Prediction ML project.
8 pages, 10 enhanced features, dark theme, fully interactive.

This file is the thin orchestrator — page logic lives in ``app/pages/``.
"""

import json
import os
import sys
import time
import uuid
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Ensure the repository root is on sys.path so the `app` package is
# importable regardless of CWD or launch method (streamlit run app/streamlit_app.py).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth_db import (  # noqa: F401 — re-exported for page modules
    USERS_DB_PATH,
    AVATAR_COLORS,
    create_user,
    delete_user,
    email_exists,
    get_user_by_username,
    hash_password,
    load_users_db,
    login_user,
    require_admin,
    save_comparison,
    save_prediction_to_history,
    save_users_db,
    track_page_visit,
    update_user_preferences,
    update_user_profile,
    username_exists,
    verify_password,
)
from app.chart_utils import apply_plotly_config, show_chart
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

warnings.filterwarnings("ignore")
CURRENT_YEAR = 2025

# =========================================================================
# Page config — must be first Streamlit command
# =========================================================================
st.set_page_config(
    page_title="AutoIntel — Car Price Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================================
# Custom CSS Injection
# =========================================================================
def inject_custom_css() -> None:
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');
    * { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }
    .stApp { background: #0c0f14; }
    section[data-testid="stSidebar"] { background: #0a0d12 !important; border-right: 1px solid rgba(232,93,4,0.15); }
    section[data-testid="stSidebar"] .stMarkdown { color: #c8ccd4; }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0c0f14; }
    ::-webkit-scrollbar-thumb { background: #e85d04; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #f48c06; }

    /* Glass card */
    .glass-card { background: rgba(20,25,40,0.85); backdrop-filter: blur(12px);
                  border: 1px solid rgba(232,93,4,0.2); border-radius: 16px; padding: 24px;
                  transition: all 0.3s ease; }
    .glass-card:hover { border-color: rgba(232,93,4,0.4); box-shadow: 0 0 20px rgba(232,93,4,0.15); transform: translateY(-2px); }

    /* KPI card */
    .kpi-card { background: rgba(20,25,40,0.9); border: 1px solid rgba(232,93,4,0.25);
                border-radius: 12px; padding: 1rem 1.25rem; text-align: center; }
    .kpi-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #e85d04; }
    .kpi-label { font-size: 0.8rem; color: #9da3b4; text-transform: uppercase; letter-spacing: 0.08em; }

    /* Gradient hero header */
    .hero-header { background: linear-gradient(135deg, #0c0f14 0%, #1a1f35 50%, #0f1520 100%);
                   border: 1px solid rgba(232,93,4,0.2); border-radius: 16px;
                   padding: 2.5rem; text-align: center; position: relative; overflow: hidden; }
    .hero-header::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
                           background: radial-gradient(circle at 30% 50%, rgba(232,93,4,0.08) 0%, transparent 60%),
                                       radial-gradient(circle at 70% 50%, rgba(72,149,239,0.06) 0%, transparent 60%);
                           animation: pulse 8s ease-in-out infinite alternate; }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); } }
    .hero-title { font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800;
                  background: linear-gradient(90deg, #e85d04, #f48c06, #4895ef);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

    /* Orange gradient button */
    .orange-btn { background: linear-gradient(135deg, #e85d04, #f48c06); color: white; border: none;
                  border-radius: 50px; padding: 0.6rem 2rem; font-family: 'Syne', sans-serif;
                  font-weight: 700; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
    .orange-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(232,93,4,0.4); }

    /* Badge classes */
    .badge-luxury { background: linear-gradient(135deg, #9b5de5, #7b2cbf); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .badge-premium { background: linear-gradient(135deg, #e85d04, #f48c06); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .badge-mid { background: linear-gradient(135deg, #4895ef, #4cc9f0); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .badge-budget { background: linear-gradient(135deg, #52b788, #40916c); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .gradient-divider { height: 2px; background: linear-gradient(90deg, transparent, #e85d04, #f48c06, transparent); margin: 16px 0; }

    /* Auth card (glass-morphism) */
    .auth-card { background: rgba(20,25,40,0.95); border: 1px solid rgba(232,93,4,0.3);
                 border-radius: 20px; padding: 2.5rem;
                 box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(232,93,4,0.08); }

    /* Avatar circle */
    .avatar-circle { width: 80px; height: 80px; border-radius: 50%;
                     display: flex; align-items: center; justify-content: center;
                     font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800;
                     color: white; margin: 0 auto 1rem;
                     box-shadow: 0 0 20px rgba(232,93,4,0.3); }

    /* Price reveal shimmer animation */
    @keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
    .price-reveal { font-family: 'Syne', sans-serif; font-size: 3.5rem; font-weight: 800;
                    background: linear-gradient(90deg, #e85d04 0%, #f48c06 30%, #ffffff 50%, #f48c06 70%, #e85d04 100%);
                    background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    background-clip: text; animation: shimmer 2s linear infinite; }

    /* Password strength bar */
    .pwd-strength { background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; margin: 4px 0; overflow: hidden; }
    .pwd-bar { height: 100%; border-radius: 4px; transition: width 0.3s ease, background 0.3s ease; }

    /* Sidebar nav active */
    .nav-active { border-left: 3px solid #e85d04; background: rgba(232,93,4,0.1); border-radius: 0 8px 8px 0; }

    /* Progress bar gradient */
    [data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #e85d04, #f48c06) !important; }

    /* Metric container */
    [data-testid="metric-container"] { background: rgba(20,25,40,0.85); border: 1px solid rgba(232,93,4,0.2);
                                        border-radius: 12px; padding: 1rem; }
    [data-testid="stMetricValue"] { font-family: 'Syne', sans-serif; color: #e85d04 !important; font-size: 1.8rem !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: rgba(10,13,18,0.8); border-bottom: 1px solid rgba(232,93,4,0.2);
                                         border-radius: 12px 12px 0 0; padding: 4px 4px 0; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; padding: 8px 16px !important;
                                    color: #9da3b4 !important; font-size: 0.85rem !important; }
    .stTabs [aria-selected="true"] { background: rgba(232,93,4,0.2) !important; color: #e85d04 !important;
                                      border-bottom: 2px solid #e85d04 !important; }

    /* Input fields dark styling */
    .stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div {
      background: rgba(20,25,40,0.9) !important;
      border: 1px solid rgba(255,255,255,0.1) !important;
      color: #e8eaf0 !important;
      border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus { border-color: #e85d04 !important; box-shadow: 0 0 0 1px rgba(232,93,4,0.3) !important; }

    /* Button styling */
    .stButton button { background: linear-gradient(135deg, #e85d04, #f48c06) !important; color: white !important;
                       border: none !important; border-radius: 25px !important; padding: 8px 24px !important;
                       font-weight: 600 !important; transition: all 0.3s ease !important; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(232,93,4,0.4) !important; }

    /* Dataframe */
    [data-testid="stDataFrame"] { background: transparent !important; }
    [data-testid="stDataFrame"] th { background: #1a1d24 !important; color: #e85d04 !important; }
    [data-testid="stDataFrame"] td { background: rgba(255,255,255,0.02) !important; color: #c8ccd4 !important; border-color: rgba(255,255,255,0.05) !important; }
    [data-testid="stDataFrame"] tr:nth-child(even) td { background: rgba(255,255,255,0.04) !important; }

    /* Expander */
    .stExpander { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px !important; }

    /* Shared class for marketing hero */
    .hero-text { font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #e85d04, #f48c06, #4895ef);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; }
    </style>
    """,
        unsafe_allow_html=True,
    )


# =========================================================================
# Session State Init
# =========================================================================
def init_session_state() -> None:
    defaults = {
        "page": "🏠 Dashboard Home",
        "last_prediction": {},
        "page_visits": {},
        "global_filters": {},
        "last_pred_inputs": {},
        "ab_mode": False,
        "ab_car1": {},
        "ab_car2": {},
        "authenticated": False,
        "user": {},
        "auth_page": "login",
        "session_id": str(uuid.uuid4()),
        "current_page": "Dashboard",
        "last_model": "xgboost",
        "last_prediction_inputs": {},
        "last_prediction_result": None,
        "global_company_filter": [],
        "global_fuel_filter": [],
        "global_year_range": (2000, 2024),
        "expert_mode": False,
        "comparison_car_a": None,
        "comparison_car_b": None,
        "login_attempts": 0,
        "login_lock_time": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# =========================================================================
# Cache Functions
# =========================================================================
@st.cache_data(show_spinner="📦 Loading car dataset...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/Cleaned_Car_data.csv", index_col=0)
    df["car_age"] = CURRENT_YEAR - df["year"]
    df["price_tier"] = pd.cut(
        df["Price"],
        bins=[0, 300000, 800000, 2000000, 1e8],
        labels=["Budget", "Mid-range", "Premium", "Luxury"],
    )
    return df


@st.cache_resource(show_spinner="🧠 Loading preprocessor...")
def load_preprocessor() -> object:
    return joblib.load("ml_ready/preprocessor.pkl")


@st.cache_resource(show_spinner="🤖 Loading ML models...")
def load_models() -> dict[str, object]:
    models = {}
    model_dir = "ml_ready/models"
    model_map = {
        "gradient_boosting.pkl": "Gradient Boosting",
        "xgboost.pkl": "XGBoost",
        "random_forest.pkl": "Random Forest",
        "linear_regression.pkl": "Linear Regression",
        "ridge.pkl": "Ridge",
        "svr.pkl": "SVR",
        "lasso.pkl": "Lasso",
        "knn.pkl": "KNN",
    }
    for fname in os.listdir(model_dir):
        if fname in model_map:
            models[model_map[fname]] = joblib.load(os.path.join(model_dir, fname))
    return models


@st.cache_resource(show_spinner="📊 Loading model results...")
def load_gs_results() -> dict[str, object]:
    results = {}
    for fname in [
        "gradient_boosting_gs_results.json",
        "xgboost_gs_results.json",
        "random_forest_gs_results.json",
    ]:
        path = f"ml_ready/models/{fname}"
        if os.path.exists(path):
            with open(path) as f:
                results[fname.replace("_gs_results.json", "")] = json.load(f)
    return results


@st.cache_data(ttl=3600, show_spinner="📐 Loading preprocessed data...")
def load_preprocessed() -> dict[str, object]:
    return {
        "X_train": np.load("ml_ready/X_train.npy"),
        "X_test": np.load("ml_ready/X_test.npy"),
        "y_train": np.load("ml_ready/y_train.npy"),
        "y_test": np.load("ml_ready/y_test.npy"),
        "y_train_orig": np.load("ml_ready/y_train_original.npy"),
        "y_test_orig": np.load("ml_ready/y_test_original.npy"),
        "feature_names": np.load("ml_ready/feature_names.npy", allow_pickle=True),
    }


# =========================================================================
# Sidebar
# =========================================================================
def render_sidebar() -> None:
    user = st.session_state.get("user", {})
    first_name = user.get("full_name", "User").split()[0] if user.get("full_name") else "User"
    avatar_color = user.get("avatar_color", "#e85d04")
    initials = (
        "".join(w[0].upper() for w in user.get("full_name", "U").split()[:2])
        if user.get("full_name")
        else "U"
    )
    role = user.get("role", "user")
    login_count = user.get("login_count", 1)

    with st.sidebar:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:8px">'
            f'<div class="avatar-circle" style="background:{avatar_color};width:60px;height:60px;font-size:1.4rem;margin:0 auto">'
            f"<span>{initials}</span></div>"
            f'<p style="color:#e8eaf0;font-weight:600;margin:6px 0 0;font-size:0.95rem">Hi, {first_name}!</p>'
            f'<p style="color:#9da3b4;font-size:0.7rem;margin:0">{"👑 Admin" if role == "admin" else "👤 User"} · {login_count} logins</p>'
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p style="font-family:Syne;font-size:1.8rem;font-weight:800;background:linear-gradient(90deg,#e85d04,#f48c06);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin:0">🚗 AutoIntel</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr style="border:1px solid rgba(232,93,4,0.2)">', unsafe_allow_html=True)

        nav_items = [
            "🏠 Dashboard",
            "📊 Dataset Explorer",
            "🔍 EDA Deep-Dive",
            "🤖 Model Lab",
            "🧪 Residual Analysis",
            "🔮 Price Predictor",
            "📈 Market Intelligence",
            "⚙️ Pipeline Inspector",
            "👤 My Profile",
        ]
        if role == "admin" and require_admin():
            nav_items.append("🛡️ Admin Panel")

        current_page = st.session_state.get("current_page", "Dashboard")
        for item in nav_items:
            is_active = current_page == item
            if st.button(item, key=f"nav_{item}", use_container_width=True, type="secondary"):
                st.session_state.current_page = item
                st.rerun()
            style_css = f"""<style>
            div.stButton button[key="nav_{item}"] {{
                background: {"rgba(232,93,4,0.15)" if is_active else "transparent"} !important;
                color: {"#e85d04" if is_active else "#c8ccd4"} !important;
                border-left: {"3px solid #e85d04" if is_active else "3px solid transparent"} !important;
                text-align: left !important; border-radius: 0 !important;
                justify-content: left !important; padding: 8px 16px !important;
            }}
            </style>"""
            st.markdown(style_css, unsafe_allow_html=True)

        st.markdown('<hr style="border:1px solid rgba(232,93,4,0.2)">', unsafe_allow_html=True)

        with st.expander("⚡ Quick Stats", expanded=False):
            col1, col2 = st.columns(2)
            col1.metric("Records", "11,149")
            col2.metric("Models", "5" if not demo_mode else "⚠️ Demo")
            col1.metric("Your Preds", str(len(user.get("prediction_history", []))))
            col2.metric("Version", "6.0")

        with st.expander("🎛️ Global Filters", expanded=False):
            st.session_state.global_filters["company"] = st.multiselect(
                "Company", companies if not demo_mode else [], key="gf_comp"
            )
            st.session_state.global_filters["fuel"] = st.multiselect(
                "Fuel", fuel_types if not demo_mode else [], key="gf_fuel"
            )
            gcol1, gcol2 = st.columns(2)
            if gcol1.button("Apply", use_container_width=True):
                st.rerun()
            if gcol2.button("Reset", use_container_width=True):
                st.session_state.global_filters = {"company": [], "fuel": []}
                st.rerun()

        expert = st.toggle("⚡ Expert Mode", value=st.session_state.get("expert_mode", False))
        if expert != st.session_state.get("expert_mode"):
            st.session_state.expert_mode = expert
            if user.get("user_id"):
                update_user_preferences(user["user_id"], {"expert_mode": expert})
        if expert:
            st.markdown(
                '<span style="color:#e85d04;font-size:0.7rem">⚡ Expert</span>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="border:1px solid rgba(232,93,4,0.2)">', unsafe_allow_html=True)

        st.markdown(
            '<div style="font-size:0.75rem;color:#9da3b4;text-align:center">'
            "📅 Data processed: Jun 2024<br>"
            "🧠 Trained on: 8,919 samples<br>"
            '<hr style="border:1px solid rgba(232,93,4,0.1);margin:8px 0">'
            "Built using Streamlit<br>"
            "v6.0 · MIT License</div>",
            unsafe_allow_html=True,
        )

        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# =========================================================================
# Load shared data
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
    np.random.seed(42)
    n = 200
    df = pd.DataFrame(
        {
            "name": [f"Demo Car {i}" for i in range(n)],
            "company": np.random.choice(["Maruti", "Hyundai", "Honda", "Toyota", "BMW"], n),
            "year": np.random.randint(2000, 2025, n),
            "Price": np.random.lognormal(mean=13, sigma=0.8, size=n),
            "kms_driven": np.random.randint(1000, 200000, n),
            "fuel_type": np.random.choice(["Petrol", "Diesel", "CNG"], n, p=[0.6, 0.35, 0.05]),
        }
    )
    df["car_age"] = CURRENT_YEAR - df["year"]
    df["price_tier"] = pd.cut(
        df["Price"],
        bins=[0, 300000, 800000, 2000000, 1e8],
        labels=["Budget", "Mid-range", "Premium", "Luxury"],
    )
    preprocessor = None
    models = {}
    pp_data = {
        "X_test": np.random.randn(50, 39),
        "y_test": np.random.randn(50),
        "y_test_orig": np.random.lognormal(mean=13, sigma=0.8, size=50),
        "feature_names": np.array([f"feature_{i}" for i in range(39)]),
    }
    gs_results = {}
    st.info(
        "🔧 Running in **Demo Mode** — predictions will use synthetic data. Place the full dataset in `ml_ready/` for production use."
    )

inject_custom_css()

companies = sorted(df["company"].unique())
fuel_types = sorted(df["fuel_type"].unique())


# =========================================================================
# Import page modules & inject shared globals
# =========================================================================
from app.pages import (  # noqa: E402
    admin as _admin_mod,
    auth as _auth_mod,
    dashboard as _dash_mod,
    dataset_explorer as _de_mod,
    eda as _eda_mod,
    market as _market_mod,
    model_lab as _mlab_mod,
    pipeline as _pipe_mod,
    predictor as _pred_mod,
    profile as _profile_mod,
    residuals as _res_mod,
)

# Inject shared state into ML page modules
_inject = {
    "df": df,
    "models": models,
    "preprocessor": preprocessor,
    "pp_data": pp_data,
    "gs_results": gs_results,
    "companies": companies,
    "fuel_types": fuel_types,
    "demo_mode": demo_mode,
    "CURRENT_YEAR": CURRENT_YEAR,
}

for _mod in [_dash_mod, _de_mod, _eda_mod, _mlab_mod, _res_mod, _pred_mod, _market_mod, _pipe_mod]:
    for _k, _v in _inject.items():
        setattr(_mod, _k, _v)


# =========================================================================
# Auth gate + page routing
# =========================================================================
page = st.session_state.get("current_page", st.session_state.get("page", "Dashboard"))

if not st.session_state.get("authenticated", False):
    auth_page = st.session_state.get("auth_page", "login")
    if auth_page == "signup":
        _auth_mod.render_signup_page()
    elif auth_page == "forgot":
        _auth_mod.render_forgot_password_page()
    else:
        _auth_mod.render_login_page()
        db = load_users_db()
        if not username_exists(db, "demo"):
            create_user(db, "demo", "demo@example.com", "demo123", "Demo User")
    st.stop()

track_page_visit(
    st.session_state.user.get("user_id", ""),
    st.session_state.get("current_page", "Dashboard"),
)

render_sidebar()

if demo_mode:
    st.warning(
        "⚠️ **Demo Mode** — ML model files not found. Using synthetic data and heuristic predictions."
    )

page_map = {
    "Dashboard": _dash_mod.page_dashboard_home,
    "Dataset Explorer": _de_mod.page_dataset_explorer,
    "EDA Deep-Dive": _eda_mod.page_eda_deepdive,
    "Model Lab": _mlab_mod.page_model_comparison,
    "Residual Analysis": _res_mod.page_residual_analysis,
    "Price Predictor": _pred_mod.page_price_predictor,
    "Market Intelligence": _market_mod.page_market_intelligence,
    "Pipeline Inspector": _pipe_mod.page_pipeline_inspector,
    "My Profile": _profile_mod.render_profile_page,
    "Admin Panel": _admin_mod.render_admin_panel,
}

if page == "Admin Panel" and not require_admin():
    st.error("⛔ Access denied. Admin privileges required.")
    st.session_state.current_page = "Dashboard"
    st.rerun()

renderer = page_map.get(page, _dash_mod.page_dashboard_home)
renderer()

st.session_state.page_visits[page] = st.session_state.page_visits.get(page, 0) + 1
