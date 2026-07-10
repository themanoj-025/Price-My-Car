# Database Map — Price-My-Car

## Data Storage
No database is used. Data stored as files:

| File | Format | Purpose |
|------|--------|---------|
| `Cleaned_Car_data.csv` | CSV | Training dataset (11,149 records) |
| `users_db.json` | JSON | User accounts and prediction history |
| `ml_ready/X_train.npy` | NumPy | Preprocessed training features |
| `ml_ready/X_test.npy` | NumPy | Preprocessed test features |
| `ml_ready/y_train.npy` | NumPy | Log-transformed training targets |
| `ml_ready/y_test.npy` | NumPy | Log-transformed test targets |
| `ml_ready/preprocessor.pkl` | Pickle | Fitted ColumnTransformer |

## Model Artifacts
| File | Format | Purpose |
|------|--------|---------|
| `ml_ready/models/*.pkl` | Pickle | 8 trained ML models |
| `ml_ready/feature_names.pkl` | Pickle | Feature names array |

## Entities
| Entity | Storage | Fields |
|--------|---------|--------|
| Users | `users_db.json` | user_id, username, email, password_hash, role, preferences, prediction_history |
| Car Data | CSV + NumPy | name, company, year, Price, kms_driven, fuel_type, car_age |
