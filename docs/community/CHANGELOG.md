# Changelog

All notable changes to **Price-My-Car** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-01

### Added

#### Machine Learning Pipeline
- Multi-model training pipeline with 6+ regression algorithms
- Models: Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost
- Hyperparameter tuning via `tune_hyperparameters.py`
- Feature engineering for Indian used car market
- Automated model selection based on R² score

#### Data Processing
- Indian car dataset with cleaned and prepared data (`Cleaned_Car_data.csv`)
- Data preprocessing pipeline with `prepare_ml_data.py`
- Feature encoding and scaling
- Outlier detection and handling
- `ml_ready/` directory with serialized preprocessor and models

#### Streamlit Application
- User-friendly car price prediction interface
- Input form for car parameters (make, model, year, km driven, fuel type, etc.)
- Real-time price predictions with confidence indicators
- Model performance comparison dashboard
- Feature importance visualization

#### Infrastructure
- Streamlit Cloud deployment ready
- CI workflow for testing (`test_helpers.py`)
- Educational notebook (`car_price_ml_comparison.ipynb`) with full analysis

---

## [0.1.0] — Initial Development

### Added
- Project scaffolding
- Dataset collection and cleaning
- Initial ML model training scripts
- Basic Streamlit app prototype
