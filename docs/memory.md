# MEMORY.md — Price-My-Car (AutoIntel)

## Project Overview
**AutoIntel** is a production-grade ML application for predicting **used car prices in the Indian market**. Features 8 ML models, 9 dashboard pages, user authentication, admin panel, and 10 enhanced features — all in a single Streamlit app.

## Business Purpose
Help car sellers and buyers estimate fair market prices for used cars in India using data-driven ML models trained on 11,149 real listings.

## Tech Stack
| Category | Technology |
|-----------|-----------|
| **Language** | Python 3.9+ |
| **Web UI** | Streamlit |
| **ML Models** | scikit-learn, XGBoost |
| **Data** | pandas, numpy |
| **Visualization** | Plotly, Matplotlib |
| **Serialization** | pickle, joblib |
| **Auth** | SHA-256 hashing (custom) |

## Architecture
```
Streamlit App (streamlit_app.py)
  ├── Auth System (login/signup)
  ├── 9 Dashboard Pages
  └── Admin Panel
       ↓
Preprocessor Pipeline (preprocessor.pkl)
  └── One-hot encoding + StandardScaler
       ↓
8 ML Models (ml_ready/models/*.pkl)
  ├── Linear Regression (R²=0.7654) 🏆
  ├── Ridge (R²=0.7605)
  ├── XGBoost (R²=0.7463)
  ├── Gradient Boosting (R²=0.7373)
  ├── SVR (R²=0.6998)
  ├── Lasso (R²=0.6585)
  ├── KNN (R²=0.6519)
  └── Random Forest (R²=0.5850)
```

## Key Features
- **Price Prediction** — Real-time predictions with confidence intervals
- **8 ML Models** — Side-by-side comparison
- **SHAP-lite Explanations** — Feature contribution waterfall
- **Deal Score Gauge** — 1-100 score comparing prediction vs market
- **Ensemble Prediction** — Weighted average of top-3 models
- **Depreciation Curve** — 5-year value forecast
- **Bulk Upload** — CSV batch predictions → Excel download
- **A/B Comparison** — Compare two cars side-by-side
- **User Profiles** — Prediction history, preferences
- **Admin Panel** — User management, usage analytics

## Dataset
- 11,149 records after removing 2,135 duplicates
- 39 engineered features after one-hot encoding
- Log-transformed target (skewness reduced from 5.64 → -0.12)

## Pages
1. **Dashboard** — KPI cards, pipeline stages, quick predict
2. **Dataset Explorer** — Filterable data table + charts
3. **EDA Deep-Dive** — 5-tab analysis (price, brands, correlations, outliers, trends)
4. **Model Lab** — Model comparison with radar charts
5. **Residual Analysis** — Error analysis per model
6. **Price Predictor** — Core prediction with all enhanced features
7. **Market Intelligence** — Price trends, depreciation calculator
8. **Pipeline Inspector** — Technical deep-dive
9. **My Profile** — User settings and history

## Deployment
- Streamlit Cloud with demo mode fallback
