# 🚗 AutoIntel v6.0 — Car Price Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-blue)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2-orange)](https://xgboost.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red)](https://streamlit.io)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?logo=streamlit&logoColor=white)](https://price-my-car.streamlit.app)
[![CI](https://img.shields.io/github/actions/workflow/status/themanoj-025/Price-My-Car/ci.yml?branch=main&label=CI&logo=github)](https://github.com/themanoj-025/Price-My-Car/actions)
[![Tests](https://img.shields.io/badge/tests-65%20passing-52b788?logo=pytest)](https://github.com/themanoj-025/Price-My-Car/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Dependabot](https://img.shields.io/badge/dependabot-enabled-025E8C?logo=dependabot)](https://github.com/themanoj-025/Price-My-Car/security/dependabot)

> **AutoIntel v6.0** — A production-ready, full-stack ML application for predicting used car prices in the Indian market. Features **8 ML models**, **9 dashboard pages**, **user authentication**, **admin panel**, and **10 enhanced features** — all in a single deployable Streamlit app.

---

## 📋 Table of Contents

- [Dataset](#-dataset)
- [Features](#-features)
- [Pages](#-pages)
- [Enhanced Features A–J](#-enhanced-features-a-j)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Results](#-results)
- [Files Overview](#-files-overview)
- [Workflow](#-workflow)
- [License](#-license)

---

## 📊 Dataset

The dataset contains **13,284 used car listings** from the Indian market with the following attributes:

| Column | Description |
|--------|-------------|
| `name` | Car model name (e.g., Maruti Swift Dzire VDI) |
| `company` | Manufacturer/brand (36 unique companies) |
| `year` | Manufacturing year (1996 – 2024) |
| `Price` | Selling price in Indian Rupees (Rs. 20,000 – Rs. 1,00,00,000) |
| `kms_driven` | Total distance driven in km |
| `fuel_type` | Fuel type: Diesel, Petrol, CNG, LPG, or Electric |

**Key stats:**
- **11,149** rows after removing **2,135** duplicate entries
- **39** engineered features after one-hot encoding
- **Log-transformed target** — Price skewness reduced from **5.64 → -0.12**
- No missing values — clean data from the start

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| 🔐 **Auth System** | Login, signup, forgot password with `users_db.json` persistence, demo user auto-creation |
| 🎨 **Dark Theme UI** | Glass-morphism cards, animated hero header, gradient accents, custom scrollbar |
| 🤖 **8 ML Models** | Linear Regression, Ridge, XGBoost, Gradient Boosting, SVR, Lasso, KNN, Random Forest |
| 🔮 **Price Predictor** | Real-time predictions with confidence intervals, depreciation curves, similar cars |
| 📊 **EDA Deep-Dive** | 5-tab analysis: price, brands, correlations, outliers, year trends with animated charts |
| 🧪 **Residual Analysis** | QQ plots, calibration curves, error-by-feature, top-20 worst predictions |
| 📈 **Market Intelligence** | Price trends, heatmaps, depreciation calculator, value finder, brand positioning |
| 👤 **User Profiles** | 6-tab profile: edit info, change password, preferences, prediction history, comparisons, danger zone |
| 🛡️ **Admin Panel** | User management, usage analytics, app settings, DB backup (admin-only) |
| ⚡ **Expert Mode** | Toggle between simplified and advanced views with full technical metrics |
| 🎯 **Model Recommender** | Recommends the best model based on your priority (accuracy, speed, explainability, or balanced) |
| 🔄 **A/B Comparison** | Compare two cars side-by-side with price deltas and feature-level diff tables |
| 📦 **Bulk Upload** | Upload CSV of cars for batch predictions → download results as Excel |
| 📉 **Drift Simulator** | Fast-forward car ages to see how prices change over time |
| 🚪 **Demo Mode** | Works with or without ML files — synthetic data fallback when models are missing |

---

## 📄 Pages

| # | Page | Description |
|---|------|-------------|
| 1 | 🏠 **Dashboard** | Hero banner with animated KPIs, 3 insight cards (Log Transform Boost, Top Predictor, Luxury Premium), pipeline timeline stages, Quick Predict widget, recent prediction history |
| 2 | 📊 **Dataset Explorer** | Multi-filter panel (company, fuel, year, price, KMs), interactive dataframe with progress bar, 4 dynamic mini-charts (price dist., fuel donut, KMs hist., year bars), Surprise Me button, CSV download |
| 3 | 🔍 **EDA Deep-Dive** | 5 tabs: Price Analysis (raw vs log histograms, percentile explorer), Brand Intelligence (top 20 brands, bubble chart, box plot comparison), Feature Correlations (heatmap, scatter matrix, VIF table), Outlier Analysis (IQR, before/after capping), Year & Mileage Trends (animated line chart, 2D density heatmap) |
| 4 | 🤖 **Model Lab** | Summary metrics table with color-coded R², 4 visual tabs (R² bar, RMSE/MAE grouped, Speed vs Accuracy scatter, radar chart), hyperparameter tuning results, log transform impact, model recommendation engine |
| 5 | 🧪 **Residual Analysis** | Model selector, residual scatter colored by error, residual distribution with μ±σ, QQ plot for normality, error-by-company bar chart, calibration curve, top-20 worst predictions, error vs features |
| 6 | 🔮 **Price Predictor** | Company/car/year/KMs/fuel inputs, model selection, confidence interval slider, showcase result card with shimmer animation, depreciation curve, Smart Price Explainer, Deal Score gauge, Ensemble prediction, SHAP-lite waterfall, all-model comparison, similar cars, A/B comparison mode, bulk CSV upload with Excel download, drift simulator |
| 7 | 📈 **Market Intelligence** | Price trend forecast (2025–2027), brand×year heatmap, depreciation calculator (3 cars), best value finder by budget, brand tier positioning chart, price alert simulator with deal verdict, brand positioning quadrant |
| 8 | ⚙️ **Pipeline Inspector** | Interactive 8-stage pipeline diagram, preprocessing stats table, feature engineering explainer, log transform deep-dive with Box-Cox slider, training data profiler, 8 model cards with architecture details, environment info, portfolio links |
| 9 | 👤 **My Profile** | Avatar card with initials, 6 tabs: Edit Profile, Change Password, Preferences, Prediction History (with mini line chart), Saved Comparisons, Danger Zone (delete account) |
| — | 🛡️ **Admin Panel** | Visible only to admin users. 3 tabs: All Users (table + CSV export), Usage Analytics (total predictions, model usage pie chart), App Settings (version, DB path, backup download, clear all histories) |

---

## ✨ Enhanced Features A–J

| Feature | Location | Description |
|---------|----------|-------------|
| **A — Smart Price Explainer** | Page 6 | Natural language breakdown of why a car is priced the way it is, based on feature contributions |
| **B — Deal Score Gauge** | Page 6 | Speedometer gauge (1–100) comparing predicted price vs market median for similar cars |
| **C — Ensemble Confidence** | Page 6 | Weighted average of top-3 models with spread indicator (green/yellow/red) for prediction reliability |
| **D — SHAP-lite Waterfall** | Page 6 | Waterfall chart showing how each feature contributes (positively or negatively) to the final price |
| **E — Data Quality Report** | Pages 1, 2 | Auto-generated badge showing null count, duplicates removed, outliers capped, fuel types grouped |
| **F — Bulk Predict Upload** | Page 6 | Upload CSV with car specs → run all models → download results as `.xlsx` with ensemble avg |
| **G — Drift Simulator** | Page 6 | Fast-forward years to see how aging affects price distribution for the entire market |
| **H — A/B Comparison** | Page 6 | Side-by-side inputs for two cars with winner badge, price delta, and feature-level diff table |
| **I — Expert Mode** | Sidebar | Toggle to show/hide R² scores, RMSE, statistical terms — switches to plain English in Simple Mode |
| **J — Price History Simulation** | Page 6 | Plot historical price trends from manufacture year, highlighting the best/worst years to buy |

---

## 🔐 Authentication System

AutoIntel v6.0 includes a complete authentication system:

- **Login**: Glass-morphism card with form validation, login lockout after 5 failed attempts, demo credentials hint
- **Signup**: Full Name, Username (3+ chars, alphanumeric), Email (format check), Password (6+ chars), Confirm Password match, Terms agreement → auto-login on success
- **Forgot Password**: Email check with status message (portfolio project — no actual email sending)
- **Demo User**: Auto-created on first run: username `demo`, password `demo123`
- **Persistence**: All user data stored in `users_db.json` — accounts, profiles, prediction history, preferences, comparisons, page visits
- **Admin**: First user to sign up gets `role: "admin"` and sees the Admin Panel in the sidebar
- **Session**: Auth state persists via Streamlit session state until browser close or logout

---

## 📁 Project Structure

```
├── Cleaned_Car_data.csv          # Raw dataset (11,149 records)
│
├── prepare_ml_data.py            # Preprocessing pipeline → ml_ready/
├── generate_report.py            # EDA report generator → report_output/
├── create_notebook.py            # ML comparison notebook builder
├── train_dashboard_models.py     # Train & save models for dashboard
├── tune_hyperparameters.py       # GridSearchCV for GB, XGBoost, RF
├── helpers.py                    # Pure helper functions (testable, no Streamlit deps)
├── test_helpers.py               # 65 unit tests for helpers
├── streamlit_app.py              # Single-file Streamlit dashboard (auth + 9 pages + admin)
├── setup.sh                      # Streamlit Cloud bootstrap script
│
├── .streamlit/config.toml        # Streamlit Cloud deployment config
├── .github/workflows/ci.yml      # GitHub Actions CI pipeline
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── .gitattributes                # Line ending config
├── LICENSE                       # MIT License
├── README.md                     # This file
│
├── ml_ready/                     # Preprocessed data & models (generated by scripts)
│   ├── X_train.npy / X_test.npy
│   ├── y_train.npy / y_test.npy
│   ├── y_train_original.npy / y_test_original.npy
│   ├── feature_names.npy
│   ├── preprocessor.pkl
│   └── models/
│       ├── linear_regression.pkl
│       ├── ridge.pkl
│       ├── xgboost.pkl
│       ├── gradient_boosting.pkl
│       ├── random_forest.pkl
│       ├── svr.pkl
│       ├── lasso.pkl
│       └── knn.pkl
│
├── report_output/                # Generated EDA report
│   ├── car_price_eda_report.html
│   └── images/                   # 14 visualization charts
│
└── car_price_ml_comparison.ipynb # Full ML algorithm comparison
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/themanoj-025/Price-My-Car.git
cd car-price-prediction

# 2. (Recommended) Create a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run streamlit_app.py
```

---

## 🚀 Usage

### 🌐 Live Demo (Streamlit Cloud)

Deploy to Streamlit Cloud in one click:

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://price-my-car.streamlit.app)

The app auto-generates the required `.npy` cache files on first deploy via `setup.sh`. All 8 models and the preprocessor are pre-trained and included in the repository.

**Login credentials:** username = `demo`, password = `demo123` (auto-created on first run)

### 1. Data Preprocessing

```bash
python prepare_ml_data.py
```

**What it does:**
- Removes duplicate rows
- Creates `car_age` feature from year
- Groups rare fuel types (CNG, LPG, Electric → Alternative)
- Caps `kms_driven` outliers at the 99th percentile
- One-hot encodes `company` (36 brands) and `fuel_type_simple`
- Scales numerical features with `StandardScaler`
- Applies **log1p-transform** to Price (reduces skewness 5.64 → -0.12)
- Saves processed data to `ml_ready/` as `.npy` and `.csv` files
- Also saves original (untransformed) Price as `y_train_original.npy` / `y_test_original.npy`
- Saves the `ColumnTransformer` preprocessor as `preprocessor.pkl`

**Output:** 39 features, 8,919 training samples, 2,230 test samples.

> **Note:** All models are trained on log-transformed Price. Predictions are inverted back to INR via `np.expm1()`.

### 2. Exploratory Data Analysis Report

```bash
python generate_report.py
```

**Opens:** `report_output/car_price_eda_report.html`

### 3. ML Model Comparison (Notebook)

```bash
# Generate the notebook
python create_notebook.py

# Execute it
jupyter nbconvert --to notebook --execute car_price_ml_comparison.ipynb --output car_price_ml_comparison_executed.ipynb

# Or open in Jupyter
jupyter notebook car_price_ml_comparison.ipynb
```

### 4. Interactive Dashboard

```bash
streamlit run streamlit_app.py
```

Opens at **http://localhost:8501** — login with demo/demo123 or create your own account.

---

## 📊 Model Performance

| # | Algorithm | Test R² | RMSE | MAE | Training Time |
|---|-----------|---------|------|-----|---------------|
| 1 | **Linear Regression** 🏆 | **0.7654** | Rs. 247,535 | Rs. 136,979 | 0.04s |
| 2 | Ridge (tuned) | 0.7605 | Rs. 250,108 | Rs. 136,875 | 0.02s |
| 3 | **XGBoost** (tuned: lr=0.1, depth=3, n_est=300) | **0.7463** | Rs. 257,436 | Rs. 131,764 | 0.84s |
| 4 | Gradient Boosting (tuned: lr=0.05, depth=5, n_est=200) | 0.7373 | Rs. 261,980 | Rs. 132,826 | 3.74s |
| 5 | SVR | 0.6998 | Rs. 280,045 | Rs. 137,355 | 26.32s |
| 6 | Lasso | 0.6585 | Rs. 298,705 | Rs. 145,382 | 0.06s |
| 7 | KNN | 0.6519 | Rs. 301,578 | Rs. 150,841 | 0.00s |
| 8 | Random Forest (tuned: depth=15, n_est=300) | 0.5850 | Rs. 329,250 | Rs. 147,945 | 1.77s |

> **Key improvement:** Log-transforming Price boosted Linear Regression from R² 0.66 → **0.77**, making it the top performer. XGBoost remains the best tree-based model with tuned hyperparameters.

### Key Findings

1. **Log-transforming Price was the biggest improvement** — reduced skewness from 5.64 → -0.12, boosting Linear Regression from R² 0.66 → **0.77**
2. **Linear models (LR, Ridge) now outperform tree models** — after log-transform, linear models capture the relationship more effectively
3. **XGBoost is the best tree-based model** (R² = 0.7463) with tuned hyperparameters (depth=3, lr=0.1, n_est=300, subsample=0.8)
4. **Car age is the strongest predictor** — newer cars command much higher prices
5. **Brand matters** — Luxury brands (Audi, BMW, Mercedes) have significantly higher average prices
6. **Hyperparameter tuning improved XGBoost** from 0.7359 → 0.7463 (+0.0104 R²)

### Feature Importance (Top 5)

1. `car_age` — ⭐ Most important (how old the car is)
2. `kms_driven` — Total distance driven
3. Company (various one-hot encoded features)
4. Fuel type (Diesel vs Petrol vs Alternative)

---

## 📄 Files Overview

| File | Description | Run Command |
|------|-------------|-------------|
| `Cleaned_Car_data.csv` | Raw dataset (11,149 records) | — |
| `prepare_ml_data.py` | Preprocessing, log-transform & feature engineering | `python prepare_ml_data.py` |
| `generate_report.py` | EDA report with 9+ visualizations | `python generate_report.py` |
| `create_notebook.py` | Generates the comparison notebook | `python create_notebook.py` |
| `tune_hyperparameters.py` | GridSearchCV for GB, XGBoost, RF | `python tune_hyperparameters.py` |
| `train_dashboard_models.py` | Trains tuned models for the dashboard | `python train_dashboard_models.py` |
| `helpers.py` | Pure helper functions (testable, no Streamlit deps) | Imported by `streamlit_app.py` |
| `test_helpers.py` | 65 unit tests for all helpers | `pytest test_helpers.py` |
| `streamlit_app.py` | Single-file dashboard (auth + 9 pages + admin) | `streamlit run streamlit_app.py` |
| `setup.sh` | Streamlit Cloud bootstrap script | Auto-runs on deploy |
| `requirements.txt` | Python dependencies | `pip install -r requirements.txt` |
| `.streamlit/config.toml` | Streamlit Cloud deployment config | — |
| `.github/workflows/ci.yml` | GitHub Actions CI pipeline | Auto-triggered on push |

---

## 🔄 Workflow

```
                          ┌─────────────────────┐
                          │  Cleaned_Car_data.csv│
                          └─────────┬───────────┘
                                    │
                          ┌─────────▼───────────┐
                          │  prepare_ml_data.py │
                          │  (log1p transform)  │
                          └─────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────────┐
                    │               │                   │
         ┌──────────▼──────┐  ┌────▼──────────┐  ┌──────▼──────────────┐
         │ generate_report │  │ tune_hyperpara│  │ train_dashboard_    │
         │  → HTML report  │  │ meters.py     │  │ models.py           │
         │  + 9 charts     │  │ GridSearchCV  │  │ (tuned params)      │
         └─────────────────┘  └────┬──────────┘  └──────┬──────────────┘
                                   │                   │
                          ┌────────▼───────────┐       │
                          │ create_notebook.py │       │
                          │ (notebook w/       │       │
                          │  log-transform +   │       │
                          │  GridSearch cells) │       │
                          └────────────────────┘       │
                                   │                   │
                                   └───────┬───────────┘
                                           │
                                  ┌────────▼────────┐
                                  │ streamlit_app.py│
                                  │  → Auth gate    │
                                  │  → 9 pages      │
                                  │  → Admin panel  │
                                  │  → Predictions  │
                                  └─────────────────┘
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Dataset sourced from the Indian used car market
- Built with scikit-learn, XGBoost, Streamlit, and Plotly
- Developed with [Codebuff](https://codebuff.com) AI-assisted development
