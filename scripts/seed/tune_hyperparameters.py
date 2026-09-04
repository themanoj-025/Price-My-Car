"""
Hyperparameter Tuning with GridSearchCV
========================================
Tunes the top 3 models (Gradient Boosting, XGBoost, Random Forest)
on log-transformed Price for optimal performance.
Saves tuned models and reports best parameters + scores.
"""

import json
import os
import time
import warnings

import joblib
import numpy as np
import structlog
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV

warnings.filterwarnings("ignore")
np.random.seed(42)

logger = structlog.get_logger("tune_hyperparameters")

logger.info("hyperparameter_tuning_started")

# -- Load data (log-transformed) -------------------------------------------
X_train = np.load("ml_ready/X_train.npy")
X_test = np.load("ml_ready/X_test.npy")
y_train = np.load("ml_ready/y_train.npy")
y_test = np.load("ml_ready/y_test.npy")

logger.info("data_loaded", x_train_shape=str(X_train.shape), y_train_shape=str(y_train.shape), x_test_shape=str(X_test.shape), y_test_shape=str(y_test.shape), y_min=round(y_train.min(), 4), y_max=round(y_train.max(), 4))

# =========================================================================
# Define model-specific parameter grids
# =========================================================================

models_to_tune = {
    "Gradient Boosting": {
        "model": GradientBoostingRegressor(random_state=42),
        "param_grid": {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.05, 0.1],
            "min_samples_leaf": [2, 5],
            "subsample": [0.8, 1.0],
        },
    },
    "XGBoost": {
        "model": xgb.XGBRegressor(random_state=42, verbosity=0),
        "param_grid": {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 6, 9],
            "learning_rate": [0.05, 0.1, 0.2],
            "subsample": [0.8, 1.0],
            "colsample_bytree": [0.8, 1.0],
        },
    },
    "Random Forest": {
        "model": RandomForestRegressor(random_state=42, n_jobs=-1),
        "param_grid": {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 15, None],
            "min_samples_leaf": [2, 5],
            "min_samples_split": [2, 5],
        },
    },
}

# =========================================================================
# Run GridSearchCV for each model
# =========================================================================

tuning_results = []
best_models = {}
os.makedirs("ml_ready/models", exist_ok=True)

for model_name, config in models_to_tune.items():
    n_combos = 1
    for v in config["param_grid"].values():
        n_combos *= len(v)
    logger.info("tuning_model", model=model_name, combinations=n_combos, fits=n_combos * 3)

    start_time = time.time()

    gs = GridSearchCV(
        estimator=config["model"],
        param_grid=config["param_grid"],
        cv=3,
        scoring="r2",
        n_jobs=-1,
        verbose=1,
        return_train_score=True,
    )

    gs.fit(X_train, y_train)

    elapsed = time.time() - start_time

    # Evaluate on test set
    y_pred = gs.best_estimator_.predict(X_test)
    y_pred_train = gs.best_estimator_.predict(X_train)

    # Convert back to original price scale for metrics
    y_test_orig = np.expm1(y_test)
    y_pred_orig = np.expm1(y_pred)
    y_train_pred_orig = np.expm1(y_pred_train)
    y_train_orig = np.expm1(y_train)

    test_r2 = r2_score(y_test_orig, y_pred_orig)
    rmse = np.sqrt(mean_squared_error(y_test_orig, y_pred_orig))
    mae = mean_absolute_error(y_test_orig, y_pred_orig)
    train_r2 = r2_score(y_train_orig, y_train_pred_orig)

    # Also report log-space R² (what GridSearchCV optimized)
    test_r2_log = r2_score(y_test, y_pred)
    train_r2_log = r2_score(y_train, y_pred_train)
    cv_score = gs.best_score_  # This is CV mean R² in log-space

    logger.info("tuning_done", model=model_name, elapsed_s=round(elapsed, 1), best_params=gs.best_params_)
    logger.info("log_space_performance", cv_r2=round(cv_score, 4), train_r2=round(train_r2_log, 4), test_r2=round(test_r2_log, 4))
    logger.info("original_scale_performance", train_r2=round(train_r2, 4), test_r2=round(test_r2, 4), rmse=round(rmse, 0), mae=round(mae, 0))

    # Save best model
    model_path = f"ml_ready/models/{model_name.lower().replace(' ', '_')}.pkl"
    joblib.dump(gs.best_estimator_, model_path)
    best_models[model_name] = gs.best_estimator_
    logger.info("model_saved", model=model_name, path=model_path)

    tuning_results.append(
        {
            "Model": model_name,
            "Best Params": gs.best_params_,
            "CV R² (log)": cv_score,
            "Test R² (log)": test_r2_log,
            "Test R² (orig)": test_r2,
            "RMSE (orig)": rmse,
            "MAE (orig)": mae,
            "Train R² (orig)": train_r2,
            "Tuning Time (s)": round(elapsed, 1),
        }
    )

    # Save full GridSearchCV results for analysis
    results_df_path = f"ml_ready/models/{model_name.lower().replace(' ', '_')}_gs_results.json"
    cv_results = {
        "params": [str(p) for p in gs.cv_results_["params"]],
        "mean_test_score": [round(s, 4) for s in gs.cv_results_["mean_test_score"]],
        "std_test_score": [round(s, 4) for s in gs.cv_results_["std_test_score"]],
        "mean_train_score": [round(s, 4) for s in gs.cv_results_["mean_train_score"]],
        "rank_test_score": [int(s) for s in gs.cv_results_["rank_test_score"]],
    }
    with open(results_df_path, "w") as f:
        json.dump(cv_results, f, indent=2)

# =========================================================================
# Summary
# =========================================================================
for r in sorted(tuning_results, key=lambda x: x["Test R² (orig)"], reverse=True):
    logger.info("tuning_summary", model=r['Model'], test_r2_orig=round(r['Test R² (orig)'], 4), rmse=round(r['RMSE (orig)'], 0), mae=round(r['MAE (orig)'], 0), elapsed_s=r['Tuning Time (s)'])

for r in tuning_results:
    logger.info("best_params", model=r['Model'], params=r['Best Params'])

logger.info("all_tuned_models_saved", dir="ml_ready/models/")
