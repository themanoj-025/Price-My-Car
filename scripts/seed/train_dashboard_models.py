"""
Train and save models for the Streamlit dashboard.
Uses tuned hyperparameters (from GridSearchCV) and log-transformed Price.
Models predict in log-space; predictions are inverted with np.expm1().
"""

import os
import time
import warnings

import joblib
import numpy as np
import structlog
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor

warnings.filterwarnings("ignore")

logger = structlog.get_logger("train_dashboard_models")

X_train = np.load("ml_ready/X_train.npy")
y_train = np.load("ml_ready/y_train.npy")
X_test = np.load("ml_ready/X_test.npy")
y_test = np.load("ml_ready/y_test.npy")

logger.info("training_started", y_min=round(y_train.min(), 4), y_max=round(y_train.max(), 4))

models = {}logger.info("training_gradient_boosting", lr=0.05, depth=5, n_estimators=200, subsample=0.8)
t0 = time.time()
models["Gradient Boosting"] = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    min_samples_leaf=2,
    subsample=0.8,
    random_state=42,
).fit(X_train, y_train)
logger.info("gradient_boosting_done", elapsed_s=round(time.time() - t0, 1))logger.info("training_xgboost", lr=0.1, depth=3, n_estimators=300, subsample=0.8, colsample=0.8)
t0 = time.time()
models["XGBoost"] = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=3,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=0,
).fit(X_train, y_train)
logger.info("xgboost_done", elapsed_s=round(time.time() - t0, 1))logger.info("training_random_forest", depth=15, n_estimators=300, min_samples_leaf=2)
t0 = time.time()
models["Random Forest"] = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    min_samples_leaf=2,
    min_samples_split=5,
    n_jobs=-1,
    random_state=42,
).fit(X_train, y_train)
logger.info("random_forest_done", elapsed_s=round(time.time() - t0, 1))

# Evaluate on test set (reported in original price scale)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

y_test_orig = np.expm1(y_test)

logger.info("test_performance")
for name, model in models.items():
    y_pred = np.expm1(model.predict(X_test))
    r2 = r2_score(y_test_orig, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test_orig, y_pred))
    mae = mean_absolute_error(y_test_orig, y_pred)
    logger.info("model_performance", model=name, r2=round(r2, 4), rmse=round(rmse, 0), mae=round(mae, 0))

os.makedirs("ml_ready/models", exist_ok=True)
for name, model in models.items():
    path = f"ml_ready/models/{name.lower().replace(' ', '_')}.pkl"
    joblib.dump(model, path)
    logger.info("model_saved", model=name, path=path)

logger.info("all_models_ready")
