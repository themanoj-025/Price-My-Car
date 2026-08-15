# AutoIntel v6.0 — Car Price Intelligence Platform

> A production-ready ML application for predicting used car prices in the Indian market with 8 ML models, 9 dashboard pages, and 10 enhanced features.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-blue.svg)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Tech Stack & Core Technologies](#2-tech-stack--core-technologies)
- [3. High-Level Architecture](#3-high-level-architecture)
- [4. Complete Folder Structure Tree](#4-complete-folder-structure-tree)
- [5. Exhaustive File-by-File & Folder-by-Folder Breakdown](#5-exhaustive-file-by-file--folder-by-folder-breakdown)
- [6. Data Models & Schemas](#6-data-models--schemas)
- [7. API Surface](#7-api-surface)
- [8. Configuration & Environment Variables](#8-configuration--environment-variables)
- [9. Build, Run & Deployment Instructions](#9-build-run--deployment-instructions)
- [10. Data & Control Flow Walkthroughs](#10-data--control-flow-walkthroughs)
- [11. Dependency Graph Summary](#11-dependency-graph-summary)
- [12. Testing Strategy](#12-testing-strategy)
- [13. Known Issues, Technical Debt & Assumptions](#13-known-issues-technical-debt--assumptions)
- [14. Glossary](#14-glossary)
- [15. Appendix](#15-appendix)

---

## 1. Executive Summary

**AutoIntel v6.0** is a production-ready machine learning application for predicting used car prices in the Indian market. It features 8 ML models, 9 interactive dashboard pages, user authentication, an admin panel, and 10 enhanced features — all in a single deployable Streamlit app.

**Target users**: Used car buyers/sellers in India, automotive dealerships, and data science learners.

**What problem it solves**: Used car pricing in India is opaque and variable. AutoIntel provides data-driven price predictions with confidence intervals, depreciation curves, and market intelligence to help buyers and sellers make informed decisions.

**Why it exists**: The Indian used car market is massive but lacks accessible, data-driven pricing tools. AutoIntel fills this gap with a comprehensive ML pipeline and polished UI.

*Note: The dataset contains 13,284 used car listings from the Indian market. The 8 ML models and their performance metrics are explicitly documented.*

---

## 2. Tech Stack & Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.9+ | Primary language |
| Web UI | Streamlit | 1.57 | Interactive dashboard (9 pages) |
| ML | scikit-learn | 1.7 | Model training (8 algorithms) |
| Gradient Boosting | XGBoost | 3.2 | High-performance model |
| Visualization | Plotly | — | Interactive charts |
| Data Processing | pandas, numpy | — | Data manipulation |
| Auth | bcrypt | — | Password hashing |
| Serialization | joblib | — | Model persistence |
| Testing | pytest | — | Unit tests (65 tests) |

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Streamlit App (app/streamlit_app.py)                  │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │Dashboard │  │Dataset   │  │EDA       │  │Model Lab         │   │
│  │Home      │  │Explorer  │  │Deep-Dive │  │(8 models)        │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │Residual  │  │Price     │  │Market    │  │Pipeline          │   │
│  │Analysis  │  │Predictor │  │Intel     │  │Inspector         │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    ML Pipeline                                │   │
│  │  CSV → Clean → Feature Eng → Log Transform → Scale → Train   │   │
│  │  Models: Linear, Ridge, XGBoost, GBM, SVR, Lasso, KNN, RF   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Auth System: Login, Signup, Forgot Password (JSON persist)  │   │
│  │  Admin Panel: User management, usage analytics               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Complete Folder Structure Tree

```
Price-My-Car/
├── .dockerignore
├── .editorconfig
├── .gitattributes
├── .github/
│   ├── CODEOWNERS
│   ├── copilot-instructions.md
│   ├── dependabot.yml
│   ├── ISSUE_TEMPLATE/
│   ├── labeler.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml
│       ├── codeql.yml
│       ├── gitleaks.yml
│       ├── labeler.yml
│       ├── maintenance.yml
│       ├── stale.yml
│       └── welcome.yml
├── .gitignore
├── .streamlit/
│   └── config.toml
├── .vscode/
│   └── settings.json
├── AGENTS.md
├── app/
│   ├── __init__.py
│   ├── helpers.py
│   └── streamlit_app.py
├── data/
│   └── Cleaned_Car_data.csv
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.yml
├── Dockerfile
├── docs/
│   ├── community/
│   ├── design/
│   ├── migration/
│   ├── product/
│   ├── project/
│   ├── reference/
│   └── technical/
├── LICENSE
├── Makefile
├── ml_ready/
│   ├── models/
│   │   ├── gradient_boosting_gs_results.json
│   │   ├── random_forest_gs_results.json
│   │   └── xgboost_gs_results.json
│   └── preprocessor.pkl
├── notebooks/
│   └── car_price_ml_comparison.ipynb
├── PROJECT_ANALYSIS.md
├── PROJECT_OVERVIEW.md
├── pyproject.toml
├── README.md
├── requirements.txt
├── scripts/
│   ├── admin/
│   │   ├── create_notebook.py
│   │   ├── debug_dtypes.py
│   │   └── generate_report.py
│   ├── backfills/
│   │   └── prepare_ml_data.py
│   └── seed/
│       ├── train_dashboard_models.py
│       └── tune_hyperparameters.py
├── setup.sh
└── tests/
    ├── __init__.py
    └── test_helpers.py
```

---

## 5. Exhaustive File-by-File & Folder-by-Folder Breakdown

### Root Files

#### `Price-My-Car/app/streamlit_app.py`
- **Purpose**: Single-file Streamlit dashboard (1700+ lines). Features authentication system (login/signup/forgot password with bcrypt), 9 interactive pages, admin panel, dark theme, and 10 enhanced features (deal score, ensemble prediction, SHAP approximation, data quality report, natural language explanation).

#### `Price-My-Car/app/helpers.py`
- **Purpose**: Helper functions (testable, no Streamlit deps). Includes `fmt_inr`, `get_price_tier`, `make_prediction`, `ensemble_prediction`, `shap_lite_approximation`, `compute_deal_score`, `generate_data_quality_report`, `generate_natural_language_explanation`.

#### `Price-My-Car/scripts/backfills/prepare_ml_data.py`
- **Purpose**: Preprocessing pipeline — log1p transform (skewness 5.64 → -0.12), feature engineering (39 features), train/test split. Writes `ml_ready/*.npy` + `preprocessor.pkl`.

#### `Price-My-Car/scripts/seed/tune_hyperparameters.py`
- **Purpose**: GridSearchCV for ensemble models (XGBoost, Gradient Boosting, Random Forest).

#### `Price-My-Car/scripts/seed/train_dashboard_models.py`
- **Purpose**: Trains tuned models and saves to `ml_ready/models/`.

#### `Price-My-Car/scripts/admin/generate_report.py`
- **Purpose**: EDA report generation with visualizations.

#### `Price-My-Car/scripts/admin/create_notebook.py`
- **Purpose**: Builds `notebooks/car_price_ml_comparison.ipynb` (ML algorithm comparison).

#### `Price-My-Car/scripts/admin/debug_dtypes.py`
- **Purpose**: Debugging tool — prints dtypes of the cleaned CSV.

#### `Price-My-Car/tests/test_helpers.py`
- **Purpose**: 65 unit tests for helper functions.

---

## 6. Data Models & Schemas

### Car Record

```json
{
  "name": "str — car model name",
  "company": "str — manufacturer (36 unique)",
  "year": "int — manufacturing year (1996-2024)",
  "Price": "float — selling price in INR",
  "kms_driven": "int — total distance driven",
  "fuel_type": "str — Diesel/Petrol/CNG/LPG/Electric",
  "car_age": "int — calculated age",
  "price_tier": "str — Budget/Mid-range/Premium/Luxury"
}
```

### Model Performance

| Model | Test R² | RMSE | MAE |
|-------|---------|------|-----|
| Linear Regression | 0.7654 | Rs. 247,535 | Rs. 136,979 |
| Ridge (tuned) | 0.7605 | Rs. 250,108 | Rs. 136,875 |
| XGBoost (tuned) | 0.7463 | Rs. 257,436 | Rs. 131,764 |
| Gradient Boosting | 0.7373 | Rs. 261,980 | Rs. 132,826 |
| SVR | 0.6998 | Rs. 280,045 | Rs. 137,355 |

---

## 7. API Surface

No REST API — this is a Streamlit web application.

---

## 8. Configuration & Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `SECRET_KEY` | Flask session key | Yes (for auth) |

**Demo credentials**: username = `demo`, password = `demo123`

---

## 9. Build, Run & Deployment Instructions

```bash
# Local
pip install -r requirements.txt
streamlit run app/streamlit_app.py

# Docker
docker compose up -d
```

---

## 10. Data & Control Flow Walkthroughs

### Flow 1: Price Prediction

1. User selects car details (brand, year, KMs, fuel type)
2. `app/helpers.py:make_prediction()` preprocesses input
3. Loaded model predicts log-transformed price
4. Result displayed with confidence interval and depreciation curve

### Flow 2: Deal Score

1. User inputs car details
2. `app/helpers.py:compute_deal_score()` compares predicted vs asking price
3. Score displayed with recommendation (good deal/fair/overpriced)

---

## 11. Dependency Graph Summary

```
app/streamlit_app.py → app/helpers.py → ml_ready/models/* → ml_ready/preprocessor.pkl
scripts/backfills/prepare_ml_data.py → data/Cleaned_Car_data.csv → ml_ready/
scripts/seed/train_dashboard_models.py → scripts/seed/tune_hyperparameters.py → ml_ready/models/
```

---

## 12. Testing Strategy

- **Framework**: pytest
- **Tests**: 65 unit tests in `tests/test_helpers.py`
- **Coverage**: Helper functions, prediction pipeline, data quality

---

## 13. Known Issues, Technical Debt & Assumptions

### Known Issues

1. **Indian market only**: Models trained on Indian car data.
2. **No real-time data**: Static dataset from 2024.

### Assumptions

1. **Log-transform critical**: Biggest improvement (R² 0.66 → 0.77).
2. **car_age is strongest predictor**: Correlation -0.78 with Price.

---

## 14. Glossary

| Term | Definition |
|------|-----------|
| **INR** | Indian Rupee |
| **log1p** | Natural log of (1 + x) — reduces skewness |
| **GridSearchCV** | Exhaustive hyperparameter search with cross-validation |
| **Deal Score** | Composite score comparing predicted vs asking price |

---

## 15. Appendix

### Dataset Stats

- 13,284 raw listings → 11,149 after dedup
- 36 unique manufacturers
- Price range: Rs. 20,000 – Rs. 1,00,00,000
- 39 engineered features

---

*This document was generated as part of a comprehensive project documentation effort. Last updated: August 8, 2026.*
