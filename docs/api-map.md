# API Map — Price-My-Car

## Application Type: Streamlit Web App (No REST API)
All logic runs in-process with no external API endpoints.

## Internal APIs

### Prediction Pipeline (`streamlit_app.py`)
| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `predict_price(features)` | Car features dict | Predicted price | Main prediction function |

### ML Training (`train_dashboard_models.py`)
| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `train_models(data)` | Cleaned dataset | Trained model files | Train price prediction models |

### Helpers (`helpers.py`)
| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `clean_data(data)` | Raw CSV data | Cleaned DataFrame | Data preprocessing |
| `encode_features(df)` | DataFrame | Encoded features | Feature encoding/transformation |

## Model Artifacts (saved as pickle)
| File | Purpose |
|------|---------|
| ml_ready/preprocessor.pkl | Saved preprocessing pipeline |
| ml_ready/feature_names.pkl | Saved feature names for inference |

## External Integrations
None — self-contained application with local CSV data.
