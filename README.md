# AutoIntel v6.0 — Car Price Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-blue)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2-orange)](https://xgboost.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red)](https://streamlit.io)
[![CI](https://img.shields.io/github/actions/workflow/status/themanoj-025/Price-My-Car/ci.yml?branch=main&label=CI&logo=github)](https://github.com/themanoj-025/Price-My-Car/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready ML application for predicting used car prices in the Indian market. Features 8 ML models, 9 dashboard pages, user authentication, admin panel, and 10 enhanced features — all in a single deployable Streamlit app.

---

## 📋 Table of Contents

- [Dataset](#dataset)
- [Features](#features)
- [Pages](#pages)
- [Installation](#installation)
- [Workflow](#workflow)
- [Model Performance](#model-performance)
- [Files](#files)
- [License](#-license)
- [Contributing](#-contributing)
- [Show Your Support](#-show-your-support)

---

> 📸 **Screenshot placeholder:** Add a screenshot of the Price Predictor page with a confidence interval.

---

## Dataset

The dataset contains 13,284 used car listings from the Indian market:

| Column | Description |
|--------|-------------|
| `name` | Car model name |
| `company` | Manufacturer/brand (36 unique) |
| `year` | Manufacturing year (1996–2024) |
| `Price` | Selling price in INR (Rs. 20,000 – Rs. 1,00,00,000) |
| `kms_driven` | Total distance driven in km |
| `fuel_type` | Fuel type: Diesel, Petrol, CNG, LPG, Electric |

**Key stats:** 11,149 rows after removing 2,135 duplicates, 39 engineered features, log-transformed target (skewness reduced from 5.64 to -0.12).

---

## Features

- **Auth System** — Login, signup, forgot password with JSON persistence
- **8 ML Models** — Linear Regression, Ridge, XGBoost, Gradient Boosting, SVR, Lasso, KNN, Random Forest
- **Price Predictor** — Real-time predictions with confidence intervals and depreciation curves
- **EDA Deep-Dive** — 5-tab analysis: price, brands, correlations, outliers, year trends
- **Market Intelligence** — Price trends, heatmaps, depreciation calculator, brand positioning
- **User Profiles** — Prediction history, comparisons, preferences
- **Admin Panel** — User management, usage analytics, app settings
- **Bulk Upload** — CSV batch predictions with Excel download
- **Drift Simulator** — See how prices change over time

---

## Pages

| # | Page | Description |
|---|------|-------------|
| 1 | Dashboard | Hero banner, KPIs, insight cards, Quick Predict widget |
| 2 | Dataset Explorer | Multi-filter panel, interactive dataframe, dynamic charts |
| 3 | EDA Deep-Dive | 5 analysis tabs with visualizations |
| 4 | Model Lab | Metrics table, performance charts, model recommendation |
| 5 | Residual Analysis | Residual scatter, QQ plots, calibration curves |
| 6 | Price Predictor | Predict with confidence intervals, depreciation, comparisons |
| 7 | Market Intelligence | Price trends, brand positioning, value finder |
| 8 | Pipeline Inspector | 8-stage pipeline diagram, preprocessing stats |
| 9 | My Profile | Edit info, prediction history, saved comparisons |

---

## Installation

```bash
git clone https://github.com/themanoj-025/Price-My-Car.git
cd Price-My-Car
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

**Demo credentials:** username = `demo`, password = `demo123`

> 💡 **Tip:** `setup.sh` automates environment setup and model training on first clone.

---

## Workflow

```
data/Cleaned_Car_data.csv
        ↓
  scripts/backfills/prepare_ml_data.py (log1p transform, feature engineering)
        ↓
  ┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
  │ scripts/admin/           │ scripts/seed/            │ scripts/seed/            │
  │ generate_report.py       │ tune_hyperparameters.py  │ train_dashboard_models.py│
  │ (HTML report, charts)    │ (GridSearchCV)           │ (tuned params)           │
  └──────────────────────────┴──────────────────────────┴──────────────────────────┘
                                  ↓
                    app/streamlit_app.py (auth + 9 pages + admin)
```

---

## Model Performance

| Model | Test R² | RMSE | MAE |
|-------|---------|------|-----|
| Linear Regression | 0.7654 | Rs. 247,535 | Rs. 136,979 |
| Ridge (tuned) | 0.7605 | Rs. 250,108 | Rs. 136,875 |
| XGBoost (tuned) | 0.7463 | Rs. 257,436 | Rs. 131,764 |
| Gradient Boosting | 0.7373 | Rs. 261,980 | Rs. 132,826 |
| SVR | 0.6998 | Rs. 280,045 | Rs. 137,355 |

Log-transforming Price was the biggest improvement — boosting Linear Regression from R² 0.66 to 0.77.

---

## Files

| File | Description |
|------|-------------|
| `scripts/backfills/prepare_ml_data.py` | Preprocessing, log-transform, feature engineering |
| `scripts/admin/generate_report.py` | EDA report with visualizations |
| `scripts/admin/create_notebook.py` | ML comparison notebook builder |
| `scripts/seed/tune_hyperparameters.py` | GridSearchCV for ensemble models |
| `scripts/seed/train_dashboard_models.py` | Trains tuned models for dashboard |
| `app/helpers.py` | Helper functions (testable, no Streamlit deps) |
| `tests/test_helpers.py` | 65 unit tests |
| `app/streamlit_app.py` | Single-file dashboard (auth + 9 pages + admin) |

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and open a Pull Request

---

## ⭐ Show Your Support

- ⭐ Star the repository if you found it useful
- 🐛 [Report a bug](https://github.com/themanoj-025/Price-My-Car/issues)
- 💡 [Request a feature](https://github.com/themanoj-025/Price-My-Car/issues)
