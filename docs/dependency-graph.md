# Dependency Graph — Price-My-Car

## Module Dependency Map

```
streamlit_app.py
  ├── helpers.py
  │     ├── pandas
  │     ├── numpy
  │     └── sklearn
  └── ml_ready/
        ├── preprocessor.pkl
        └── feature_names.pkl

train_dashboard_models.py
  ├── helpers.py
  ├── pandas, numpy, sklearn
  ├── joblib/pickle
  └── Cleaned_Car_data.csv

tune_hyperparameters.py
  ├── train_dashboard_models.py
  ├── pandas, numpy, sklearn
  └── optuna (optional)

prepare_ml_data.py
  ├── helpers.py
  └── pandas
```

## External Dependencies
| Package | Used By | Purpose |
|---------|---------|---------|
| streamlit | streamlit_app.py | Web UI framework |
| pandas | streamlit_app.py, helpers.py, training | Data manipulation |
| numpy | helpers.py, training | Numerical computation |
| scikit-learn | helpers.py, training | ML preprocessing & models |
| joblib/pickle | training scripts | Model serialization |

## Critical Files
- **helpers.py**: Shared data utilities — used by most modules
- **streamlit_app.py**: User-facing application — high impact
- **Cleaned_Car_data.csv**: Core dataset — data source
- **ml_ready/preprocessor.pkl**: Saved preprocessing pipeline — required for prediction
