# Price-My-Car — Copilot Instructions

## Code conventions
- Python with 4-space indentation
- Streamlit for dashboard, scikit-learn + XGBoost for ML
- Models serialized as .pkl files in `ml_ready/`

## Key commands
- Launch: `streamlit run app/streamlit_app.py`
- Tests: `pytest tests/test_helpers.py -v`
- Train models: `python scripts/seed/train_dashboard_models.py`
- Tune: `python scripts/seed/tune_hyperparameters.py`

## Architecture
- `app/helpers.py` — shared utility functions
- `app/streamlit_app.py` — main dashboard
- `ml_ready/` — preprocessor.pkl, feature_names.pkl, models/
- Car dataset in `data/Cleaned_Car_data.csv`
- Multiple models compared (Linear, Ridge, Lasso, KNN, SVR, RF, GB, XGB)
