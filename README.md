# 🚗 Car Price Prediction — ML Pipeline & Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-blue)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2-orange)](https://xgboost.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

End-to-end machine learning project for predicting used car prices. Includes data cleaning, exploratory data analysis, multi-model benchmarking, and an interactive Streamlit dashboard.

---

## 📋 Table of Contents

- [Dataset](#-dataset)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
  - [1. Data Preprocessing](#1-data-preprocessing)
  - [2. Exploratory Data Analysis Report](#2-exploratory-data-analysis-report)
  - [3. ML Model Comparison (Notebook)](#3-ml-model-comparison-notebook)
  - [4. Interactive Streamlit Dashboard](#4-interactive-streamlit-dashboard)
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

## 📁 Project Structure

```
├── Cleaned_Car_data.csv          # Raw dataset (11,149 records)
│
├── prepare_ml_data.py            # Preprocessing pipeline → ml_ready/
├── generate_report.py            # EDA report generator → report_output/
├── create_notebook.py            # ML comparison notebook builder
├── train_dashboard_models.py     # Train & save models for dashboard
├── streamlit_app.py              # Interactive Streamlit dashboard
│
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── .gitattributes                # Line ending config
├── LICENSE                       # MIT License
├── README.md                     # This file
│
├── ml_ready/                     # Preprocessed data & models (generated)
│   ├── X_train.npy / X_test.npy
│   ├── y_train.npy / y_test.npy
│   ├── feature_names.npy
│   ├── preprocessor.pkl
│   └── models/
│       ├── gradient_boosting.pkl
│       ├── xgboost.pkl
│       └── random_forest.pkl
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
git clone https://github.com/yourusername/car-price-prediction.git
cd car-price-prediction

# 2. (Recommended) Create a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage

### 1. Data Preprocessing

Run the preprocessing pipeline to clean data, engineer features, and split into train/test sets:

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

---

### 2. Exploratory Data Analysis Report

Generate an interactive HTML report with visualizations:

```bash
python generate_report.py
```

**Opens:** `report_output/car_price_eda_report.html`

**Report includes:**
| Chart | Description |
|-------|-------------|
| Price Distribution | Histogram + log-transformed distribution |
| Price by Fuel Type | Box & violin plots for all 5 fuel types |
| Top Companies by Price | Average price per brand |
| Price vs Car Age | Scatter colored by KMs driven |
| KMs Distribution | Histogram with summary stats |
| Year Distribution | Bar chart of manufacturing years |
| Price by Company (Top 20) | Box plots per brand |
| Correlation Heatmap | Numerical feature relationships |
| Top 10 Most Expensive Cars | Table & bar chart |

---

### 3. ML Model Comparison (Notebook)

Run the Jupyter notebook that trains and compares 8 regression algorithms with **log-transformed Price** + **hyperparameter tuning**:

```bash
# Generate the notebook
python create_notebook.py

# Execute it
jupyter nbconvert --to notebook --execute car_price_ml_comparison.ipynb --output car_price_ml_comparison_executed.ipynb

# Or open in Jupyter
jupyter notebook car_price_ml_comparison.ipynb
```

**Algorithms tested (with hyperparameter tuning via GridSearchCV):**

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

> **Key improvement:** Log-transforming Price boosted Linear Regression from R² 0.66 → **0.77**, making it the top performer. XGBoost and Gradient Boosting remain strong with tuned hyperparameters.

The notebook also generates:
- 📊 R² bar chart comparison (original INR scale)
- 📉 RMSE & MAE grouped bar chart
- 🎯 **Radar chart** — 5-dimensional model comparison
- 🔍 Feature importance (XGBoost top 15)
- 📐 Residual analysis for the best model
- 🔧 **Hyperparameter tuning** with GridSearchCV (3-fold CV) for top 3 models

---

### 4. Interactive Streamlit Dashboard

Launch the interactive web dashboard:

```bash
streamlit run streamlit_app.py
```

Opens at **http://localhost:8501**

#### Dashboard Tabs

| Tab | Features |
|-----|----------|
| 📊 **Dataset Explorer** | Filter by company, fuel type, year, price range; interactive data table with formatting; dynamic distributions (price, KMs, year, fuel breakdown); price trends by company and age |
| 📈 **EDA Visualizations** | 7 interactive Plotly charts — price distribution (raw + log), fuel type comparison (box + violin), company price comparison, price vs age scatter, KMs & year analysis, correlation heatmap, top 10 most expensive |
| 🤖 **Model Comparison** | Instant metrics table (no retraining), R² bar chart, RMSE/MAE grouped bars, radar chart image from the notebook |
| 🔮 **Price Predictor** | Select company, fuel type, manufacturing year, KMs driven, and ML model → get instant price prediction with confidence range + similar cars from dataset |

---

## 📈 Results

### Key Findings

1. **Log-transforming Price was the biggest improvement** — reduced skewness from 5.64 → -0.12, boosting Linear Regression from R² 0.66 → **0.77**
2. **Linear models (LR, Ridge) now outperform tree models** — after log-transform, linear models capture the relationship more effectively
3. **XGBoost is the best tree-based model** (R² = 0.7463) with tuned hyperparameters (depth=3, lr=0.1, n_est=300, subsample=0.8)
4. **Car age is the strongest predictor** — newer cars command much higher prices
5. **Brand matters** — Luxury brands (Audi, BMW, Mercedes) have significantly higher average prices
6. **Hyperparameter tuning improved XGBoost** from 0.7359 → 0.7463 (+0.0104 R²)
7. **Random Forest underperforms** on this tabular dataset — likely needs different preprocessing

### Feature Importance (Top 5)

1. `car_age` — ⭐ Most important (how old the car is)
2. `kms_driven` — Total distance driven
3. Company (various one-hot encoded features)
4. Fuel type (Diesel vs Petrol vs Alternative)

---

## 📄 Files Overview

| File | Description | Run Command |
|------|-------------|-------------|
| `Cleaned_Car_data.csv` | Raw dataset | — |
| `prepare_ml_data.py` | Preprocessing, log-transform & feature engineering | `python prepare_ml_data.py` |
| `generate_report.py` | EDA report with 9+ visualizations | `python generate_report.py` |
| `create_notebook.py` | Generates the comparison notebook | `python create_notebook.py` |
| `tune_hyperparameters.py` | GridSearchCV for GB, XGBoost, RF | `python tune_hyperparameters.py` |
| `train_dashboard_models.py` | Trains tuned models for the dashboard | `python train_dashboard_models.py` |
| `streamlit_app.py` | Interactive dashboard | `streamlit run streamlit_app.py` |
| `requirements.txt` | Python dependencies | `pip install -r requirements.txt` |

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
                                  │  → Dashboard    │
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
