# Price-My-Car

## Stack
- **ML:** scikit-learn + XGBoost, multiple models compared (Linear, Ridge, Lasso, KNN, SVR, RF, GB, XGB)
- **UI:** Streamlit with predictions + dashboard
- **Data:** Cleaned_Car_data.csv
- **Deployment:** Streamlit Cloud

## Dev commands
- `streamlit run streamlit_app.py` — launch dashboard
- `python test_helpers.py` — run tests
- `python train_dashboard_models.py` — train all models
- `python tune_hyperparameters.py` — hyperparameter tuning

## Key conventions
- 4-space indent for Python
- Models in `ml_ready/models/`, preprocessor in `ml_ready/preprocessor.pkl`
- `helpers.py` contains shared utility functions
- Feature names in `ml_ready/feature_names.pkl`
- No external API — fully local inference
