# Price-My-Car — Project Overview

## 1. Project Title
**Price-My-Car** — An ML-powered used car price prediction application with a Streamlit web interface, trained on a cleaned Indian car market dataset.

## 2. Executive Summary
Price-My-Car is a machine learning project that predicts the market price of used cars based on features like make, model, year, fuel type, transmission, kilometers driven, and ownership history. It uses an ensemble of regression models (Linear Regression, Lasso, Ridge, Random Forest, Gradient Boosting, XGBoost) trained on a cleaned dataset of Indian used car listings. The application provides a Streamlit web interface where users input car details and receive instant price estimates with confidence bands.

## 3. Problem Statement
Sellers and buyers in the Indian used car market lack a simple, data-driven tool to estimate fair market prices. Pricing is often based on intuition or inconsistent online listings, leading to overpricing or undervaluation. This project provides an accessible ML-based pricing tool that learns from real market data.

## 4. Objectives
- Train and compare multiple regression models for car price prediction
- Provide an easy-to-use web interface for instant price estimates
- Expose feature importance and model interpretability
- Support hyperparameter tuning for optimal performance
- Generate comparison reports between model performance

## 5. Key Features
- **Price prediction:** Input car details → get estimated market price
- **Multiple models:** Linear, Lasso, Ridge, Random Forest, Gradient Boosting, XGBoost
- **Model comparison:** Performance metrics (R², MAE, RMSE) and visual comparisons
- **Hyperparameter tuning:** Grid search and randomized search for optimal params
- **Feature preprocessing:** Automatic encoding of categorical features, scaling of numerical features
- **Report generation:** PDF/HTML reports comparing model performances
- **Data cleaning pipeline:** Raw car data → cleaned, feature-engineered dataset

## 6. System Architecture
```
User Input (Streamlit web form)
        │
        ▼
  Preprocessor Pipeline (preprocessor.pkl)
    ├── One-hot encoding (categorical: make, model, fuel, transmission, etc.)
    └── Scaling (numerical: year, km_driven, engine_cc, etc.)
        │
        ▼
  Ensemble of Trained Models (saved .pkl files)
    ├── Linear Regression / Lasso / Ridge
    ├── Random Forest / Gradient Boosting
    └── XGBoost
        │
        ▼
  Streamlit App (streamlit_app.py)
    └── Displays predicted price + confidence + model comparison
```

## 7. Tech Stack
| Category | Technology |
|---|---|
| **Language** | Python 3.x |
| **Web UI** | Streamlit |
| **ML Framework** | scikit-learn, XGBoost |
| **Data Processing** | pandas, numpy |
| **Preprocessing** | scikit-learn Pipeline, ColumnTransformer |
| **Model Serialization** | pickle (.pkl files) |
| **Visualization** | Matplotlib, Seaborn, plotly |
| **Reporting** | Jupyter notebooks, HTML export |
| **Jupyter** | Jupyter Notebook (.ipynb for EDA and experiments) |

## 8. Architecture Diagram
See Section 6 — single-component Streamlit app with pre-trained, serialized models loaded at startup.

## 9. Folder Structure
```
Price-My-Car/
├── streamlit_app.py              # Main web application
├── helpers.py                    # Helper functions (data loading, prediction, formatting)
├── prepare_ml_data.py            # Data cleaning and feature engineering pipeline
├── train_dashboard_models.py     # Model training script for dashboard models
├── tune_hyperparameters.py       # Hyperparameter tuning (GridSearch, RandomizedSearch)
├── generate_report.py            # Generate comparison reports
├── create_notebook.py            # Create Jupyter notebook from script
├── debug_dtypes.py               # Debugging script for data type issues
├── test_helpers.py               # Tests for helper functions
├── Cleaned_Car_data.csv          # Cleaned training dataset
├── ml_ready/
│   ├── preprocessor.pkl          # Fitted preprocessing pipeline
│   └── feature_names.pkl         # Feature names used by models
├── models/                       # Serialized trained models (not tracked in git)
├── requirements.txt              # Python dependencies
├── setup.sh                      # Setup script for deployment
├── car_price_ml_comparison.ipynb # Jupyter notebook with full ML pipeline
├── README.md                     # Project documentation
└── .streamlit/
    └── config.toml               # Streamlit configuration
```

## 10. Module Overview
- **streamlit_app.py:** Main UI — sidebar for input parameters, main panel for prediction results, model comparison charts
- **helpers.py:** Data loading, preprocessing, prediction aggregation, formatting utilities
- **prepare_ml_data.py:** Pipeline for converting raw car data into ML-ready format (handle missing values, encode categories, create features)
- **train_dashboard_models.py:** Training loop for multiple regression models with evaluation metrics
- **tune_hyperparameters.py:** Hyperparameter optimization using cross-validation

## 11. Database Overview
Not applicable — this project does not use a database. The dataset is stored as a single CSV file (`Cleaned_Car_data.csv`). Trained models are serialized as `.pkl` files in `ml_ready/` and `models/` directories.

Dataset fields (from Cleaned_Car_data.csv):
- Car make, model, year, fuel type, transmission, owner type, kilometers driven, mileage, engine CC, max power, seats, location, selling price (target)

## 12. API Overview
Not applicable — there is no REST API. The interface is an interactive Streamlit web form. No HTTP endpoints are exposed beyond the Streamlit server.

## 13. Authentication & Authorization
Not applicable — there is no authentication. The Streamlit app is open to all visitors.

## 14. Data Flow
1. User selects car parameters via Streamlit form (make, model, year, fuel, transmission, km driven, etc.)
2. `helpers.py` constructs a feature vector matching the training data schema
3. Feature vector passes through the saved `preprocessor.pkl` pipeline (encoding + scaling)
4. All trained models predict the price
5. Predictions are aggregated (mean, median, min, max) and displayed with confidence indicators
6. Model comparison charts show relative performance

## 15. Request Lifecycle
Not applicable — this is a Streamlit app, not a request-based API. Each user interaction triggers a full script re-run (Streamlit paradigm).

## 16. External Integrations
No external services or third-party APIs are integrated. All computation is local.

## 17. Environment Variables
No `.env.example` file found. The project does not require any environment variables.

## 18. Configuration
Minimal configuration is done via `.streamlit/config.toml` for Streamlit theme settings. Model paths and data file locations are hardcoded in the source code.

## 19. Security Measures
- No authentication, no input sanitization, no HTTPS enforcement
- This is a local/educational application with no production security measures

## 20. Logging & Monitoring
No logging or monitoring is configured. The application uses Streamlit's default output.

## 21. Error Handling
Minimal error handling — the application assumes input data is valid. Exceptions during model loading or prediction may crash the app.

## 22. Performance Optimizations
- Models are loaded once at startup and cached in memory
- Feature preprocessing uses scikit-learn Pipelines for efficiency
- No database, no caching layer, no async processing

## 23. Deployment Architecture
No deployment configuration files found (no Dockerfile, Procfile, or platform configs). Deployable on Streamlit Cloud (requires `setup.sh` for system dependencies on first run).

## 24. Testing Strategy
- **test_helpers.py:** Contains basic tests for helper functions
- No test framework (pytest) configured
- No CI pipeline

## 25. Development Workflow
No CONTRIBUTING.md found. No documented conventions.

## 26. Known Limitations
- **Indian market only:** Dataset is specific to Indian car market; predictions may not generalize
- **Static dataset:** Model is not retrained with new data; predictions become stale over time
- **No web API:** Cannot be integrated programmatically — only via Streamlit UI
- **Limited features:** No image-based assessment, no car condition evaluation
- **No authentication:** Anyone can use the app; no usage limits

## 27. Future Roadmap
No documented roadmap found. Implicit improvements from code include:
- More sophisticated ensemble methods
- Real-time data updates
- REST API for programmatic access

## 28. Troubleshooting
- **Model not found error:** Run `python train_dashboard_models.py` to train and save models
- **Preprocessor not found:** Run `python prepare_ml_data.py` first
- **Streamlit won't start:** Run `pip install -r requirements.txt` to ensure all dependencies are installed

## 29. FAQ
- **How to run locally?** `pip install -r requirements.txt && streamlit run streamlit_app.py`
- **How to retrain models?** Run `python train_dashboard_models.py` (and optionally `tune_hyperparameters.py`)
- **What car markets are supported?** Currently only the Indian market (based on the training dataset).

## 30. Contributing Guidelines
Not yet defined. No CONTRIBUTING.md file exists in the repository.

## 31. License
No license file found in the repository root.

## 32. Maintainers & Contacts
No author/maintainer information specified in source files.
