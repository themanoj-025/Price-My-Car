# Architecture — Price-My-Car

## System Architecture

```
User (Browser)
       ↓
  Streamlit Web App (streamlit_app.py)
       │
       ├── Data Loading & Preprocessing
       │     ├── Cleaned_Car_data.csv
       │     └── helpers.py (data utilities)
       │
       ├── ML Pipeline
       │     ├── train_dashboard_models.py
       │     ├── tune_hyperparameters.py
       │     ├── prepare_ml_data.py
       │     └── ml_ready/ (preprocessor.pkl, feature_names.pkl)
       │
       ├── Visualization
       │     └── Car Price ML Comparison Notebook
       │
       └── Reports
             └── generate_report.py
```

## Architecture Overview
- **Single-tier**: Streamlit monolithic web application
- **Frontend**: Streamlit renders UI server-side
- **Backend**: Same Python process handles ML inference and business logic
- **Data**: CSV file with cleaned car data
- **ML**: Pre-trained models loaded from pickle files

## Data Flow
1. User selects car features via Streamlit UI
2. Input is preprocessed using saved preprocessor (`preprocessor.pkl`)
3. Trained model predicts price
4. Result displayed back to user

## Key Components
| Component | File | Role |
|-----------|------|------|
| Web UI | streamlit_app.py | User interface for price prediction |
| Data Helpers | helpers.py | Data cleaning and utility functions |
| ML Training | train_dashboard_models.py | Train prediction models |
| Hyperparameter Tuning | tune_hyperparameters.py | Optimize model parameters |
| Data Preparation | prepare_ml_data.py | Preprocess raw data for ML |
| Report Generation | generate_report.py | Generate analysis reports |
