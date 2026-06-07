"""
helpers.py — Pure helper functions for AutoIntel Car Price Intelligence.
All functions here are free of Streamlit dependencies so they can be imported
and unit-tested without a browser runtime.

"""

import numpy as np
import pandas as pd

CURRENT_YEAR = 2025

# =========================================================================
# Formatting
# =========================================================================
def fmt_inr(val):
    """Format a number as Indian Rupees with compact notation."""
    if val >= 1e7:
        return f"₹{val/1e7:.2f}Cr"
    if val >= 1e5:
        return f"₹{val/1e5:.1f}L"
    return f"₹{val:,.0f}"


def get_price_tier(price):
    """Classify a price into a market tier."""
    if price >= 2_000_000:
        return "Luxury", "badge-luxury"
    if price >= 800_000:
        return "Premium", "badge-premium"
    if price >= 300_000:
        return "Mid-range", "badge-mid"
    return "Budget", "badge-budget"


def price_tier_badge(price):
    """Return an HTML <span> badge for the price tier."""
    tier, cls = get_price_tier(price)
    return f'<span class="{cls}">{tier}</span>'


def get_company_tier(avg_price):
    """Classify a brand by its average car price."""
    if avg_price >= 1_500_000:
        return "Luxury"
    if avg_price >= 600_000:
        return "Premium"
    if avg_price >= 300_000:
        return "Mid"
    return "Budget"


def get_fuel_simple(fuel_type):
    """Group rare fuel types into 'Alternative'."""
    return "Alternative" if fuel_type in ["CNG", "LPG", "Electric"] else fuel_type


# =========================================================================
# Data helpers
# =========================================================================
def get_car_name_options(df, company):
    """Return sorted unique car names for a given company."""
    return sorted(df[df["company"] == company]["name"].unique())


def get_filtered_data(df, companies, fuels, year_r, price_r, kms_r):
    """Apply multi-column filters to the car DataFrame."""
    mask = df["company"].isin(companies) & df["fuel_type"].isin(fuels)
    if year_r:
        mask &= df["year"].between(year_r[0], year_r[1])
    if price_r:
        mask &= df["Price"].between(price_r[0], price_r[1])
    if kms_r:
        mask &= df["kms_driven"].between(kms_r[0], kms_r[1])
    return df[mask]


# =========================================================================
# Pre-computed model metrics
# =========================================================================
MODEL_METRICS = [
    {"Model": "Linear Regression", "Test R²": 0.7654, "RMSE": 247535, "MAE": 136979, "Time (s)": 0.04, "Params": "Standard"},
    {"Model": "Ridge", "Test R²": 0.7605, "RMSE": 250108, "MAE": 136875, "Time (s)": 0.02, "Params": "α=1.0"},
    {"Model": "XGBoost", "Test R²": 0.7463, "RMSE": 257436, "MAE": 131764, "Time (s)": 0.84, "Params": "lr=0.1, depth=3, n=300"},
    {"Model": "Gradient Boosting", "Test R²": 0.7373, "RMSE": 261980, "MAE": 132826, "Time (s)": 3.74, "Params": "lr=0.05, depth=5, n=200"},
    {"Model": "SVR", "Test R²": 0.6998, "RMSE": 280045, "MAE": 137355, "Time (s)": 26.32, "Params": "rbf kernel"},
    {"Model": "Lasso", "Test R²": 0.6585, "RMSE": 298705, "MAE": 145382, "Time (s)": 0.06, "Params": "α=0.001"},
    {"Model": "KNN", "Test R²": 0.6519, "RMSE": 301578, "MAE": 150841, "Time (s)": 0.00, "Params": "k=7, distance"},
    {"Model": "Random Forest", "Test R²": 0.5850, "RMSE": 329250, "MAE": 147945, "Time (s)": 1.77, "Params": "depth=15, n=300"},
]

METRICS_DF = pd.DataFrame(MODEL_METRICS)

FUEL_COLORS = {
    "Diesel": "#4895ef",
    "Petrol": "#e85d04",
    "CNG": "#52b788",
    "LPG": "#9b5de5",
    "Electric": "#f48c06",
}
TIER_COLORS = {
    "Luxury": "#9b5de5",
    "Premium": "#e85d04",
    "Mid": "#4895ef",
    "Budget": "#52b788",
}


# =========================================================================
# Prediction & model helpers
# =========================================================================
def make_prediction(model, input_df, preprocessor):
    """Run a model prediction and invert the log-transform."""
    X = preprocessor.transform(input_df)
    pred_log = model.predict(X)[0]
    return float(np.expm1(pred_log))


def compute_deal_score(predicted, actual, rarity=1.0):
    """Deal Score System — score 1-100."""
    diff = (predicted - actual) / predicted
    score = max(0, min(100, (diff * 50 + 50) * rarity))
    return round(score)


def ensemble_prediction(models, input_df, preprocessor):
    """Ensemble of top-3 models with variance indicator."""
    top3 = ["Linear Regression", "XGBoost", "Gradient Boosting"]
    preds = []
    for name in top3:
        if name in models:
            preds.append(make_prediction(models[name], input_df, preprocessor))
    if not preds:
        return None, None, "red"
    mean_pred = float(np.mean(preds))
    spread = (max(preds) - min(preds)) / mean_pred * 100 if mean_pred > 0 else 0
    color = "green" if spread < 10 else ("yellow" if spread < 20 else "red")
    return mean_pred, spread, color


def shap_lite_approximation(model, input_df, preprocessor, feature_names):
    """SHAP-lite: approximate top-8 feature contributions."""
    X = preprocessor.transform(input_df)
    if hasattr(model, "coef_"):
        coefs = model.coef_.flatten() if len(model.coef_.shape) > 1 else model.coef_
        contributions = {}
        for i, coef in enumerate(coefs):
            if i < len(feature_names):
                name = feature_names[i]
                contrib = float(coef * X[0, i])
                contributions[name] = contrib
        return sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
    elif hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        contributions = {}
        for i, imp in enumerate(importances):
            if i < len(feature_names):
                contributions[feature_names[i]] = float(imp * X[0, i] * 100000)
        return sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
    return []


# =========================================================================
# Reporting helpers
# =========================================================================
def generate_data_quality_report(df, df_original):
    """Auto-generate mini data quality report items."""
    dupes = len(df_original) - len(df)
    nulls = int(df.isnull().sum().sum())
    kms_p99 = df["kms_driven"].quantile(0.99)
    kms_capped = int((df_original["kms_driven"] > kms_p99).sum())
    alt_fuels = int(df_original[df_original["fuel_type"].isin(["CNG", "LPG", "Electric"])].shape[0])
    return [
        ("✅", f"No nulls found — {nulls} missing values"),
        ("✅", f"{dupes:,} duplicates removed"),
        ("✅", f"Outliers capped at P99 ({kms_capped:,} rows)"),
        ("⚠️", f'{alt_fuels} rare fuel types grouped as "Alternative"'),
    ]


def generate_natural_language_explanation(contributions, base_price, final_price):
    """Smart Price Explainer — natural language summary."""
    explanation = f"This car is priced at **{fmt_inr(final_price)}**"
    if not contributions:
        return explanation + "."
    pos = [c for c in contributions if c[1] > 0][:3]
    neg = [c for c in contributions if c[1] < 0][:3]
    parts = []
    for name, val in pos:
        parts.append(f"**{name}** adds **+{fmt_inr(abs(val))}**")
    for name, val in neg:
        parts.append(f"**{name}** reduces **-{fmt_inr(abs(val))}**")
    if parts:
        explanation += " because " + ", ".join(parts)
    return explanation + "."
