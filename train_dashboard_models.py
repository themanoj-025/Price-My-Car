"""
Train and save models for the Streamlit dashboard.
Uses tuned hyperparameters (from GridSearchCV) and log-transformed Price.
Models predict in log-space; predictions are inverted with np.expm1().
"""
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import warnings, os, time
warnings.filterwarnings('ignore')

X_train = np.load('ml_ready/X_train.npy')
y_train = np.load('ml_ready/y_train.npy')
X_test = np.load('ml_ready/X_test.npy')
y_test = np.load('ml_ready/y_test.npy')

print(f"Training on log-transformed y_train (range: {y_train.min():.4f} - {y_train.max():.4f})")

models = {}

print('\nTraining Gradient Boosting (tuned: lr=0.05, depth=5, n_est=200, subsample=0.8)...')
t0 = time.time()
models['Gradient Boosting'] = GradientBoostingRegressor(
    n_estimators=200, max_depth=5, learning_rate=0.05,
    min_samples_leaf=2, subsample=0.8, random_state=42
).fit(X_train, y_train)
print(f'  Done in {time.time()-t0:.1f}s')

print('\nTraining XGBoost (tuned: lr=0.1, depth=3, n_est=300, subsample=0.8, colsample=0.8)...')
t0 = time.time()
models['XGBoost'] = xgb.XGBRegressor(
    n_estimators=300, max_depth=3, learning_rate=0.1,
    subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=0
).fit(X_train, y_train)
print(f'  Done in {time.time()-t0:.1f}s')

print('\nTraining Random Forest (tuned: depth=15, n_est=300, min_samples_leaf=2)...')
t0 = time.time()
models['Random Forest'] = RandomForestRegressor(
    n_estimators=300, max_depth=15, min_samples_leaf=2,
    min_samples_split=5, n_jobs=-1, random_state=42
).fit(X_train, y_train)
print(f'  Done in {time.time()-t0:.1f}s')

# Evaluate on test set (reported in original price scale)
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
y_test_orig = np.expm1(y_test)

print('\n--- Test Performance (original INR scale) ---')
for name, model in models.items():
    y_pred = np.expm1(model.predict(X_test))
    r2 = r2_score(y_test_orig, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test_orig, y_pred))
    mae = mean_absolute_error(y_test_orig, y_pred)
    print(f'  {name:.<20} R2: {r2:.4f}, RMSE: INR {rmse:,.0f}, MAE: INR {mae:,.0f}')

os.makedirs('ml_ready/models', exist_ok=True)
for name, model in models.items():
    path = f'ml_ready/models/{name.lower().replace(" ", "_")}.pkl'
    joblib.dump(model, path)
    print(f'Saved: {path}')

print('\nAll dashboard models ready!')
