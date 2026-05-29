"""
Hyperparameter Tuning with GridSearchCV
========================================
Tunes the top 3 models (Gradient Boosting, XGBoost, Random Forest)
on log-transformed Price for optimal performance.
Saves tuned models and reports best parameters + scores.
"""

import numpy as np
import warnings
import os
import time
import json
import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb

warnings.filterwarnings('ignore')
np.random.seed(42)

print("=" * 70)
print("HYPERPARAMETER TUNING - GridSearchCV")
print("=" * 70)

# -- Load data (log-transformed) -------------------------------------------
X_train = np.load('ml_ready/X_train.npy')
X_test = np.load('ml_ready/X_test.npy')
y_train = np.load('ml_ready/y_train.npy')
y_test = np.load('ml_ready/y_test.npy')

print(f"\nLoaded log-transformed data:")
print(f"  X_train: {X_train.shape}, y_train: {y_train.shape}")
print(f"  X_test:  {X_test.shape}, y_test:  {y_test.shape}")
print(f"  y_train range: {y_train.min():.4f} - {y_train.max():.4f}")

# =========================================================================
# Define model-specific parameter grids
# =========================================================================

models_to_tune = {
    'Gradient Boosting': {
        'model': GradientBoostingRegressor(random_state=42),
        'param_grid': {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.05, 0.1],
            'min_samples_leaf': [2, 5],
            'subsample': [0.8, 1.0]
        }
    },
    'XGBoost': {
        'model': xgb.XGBRegressor(random_state=42, verbosity=0),
        'param_grid': {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.05, 0.1, 0.2],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0]
        }
    },
    'Random Forest': {
        'model': RandomForestRegressor(random_state=42, n_jobs=-1),
        'param_grid': {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, None],
            'min_samples_leaf': [2, 5],
            'min_samples_split': [2, 5]
        }
    }
}

# =========================================================================
# Run GridSearchCV for each model
# =========================================================================

tuning_results = []
best_models = {}
os.makedirs('ml_ready/models', exist_ok=True)

for model_name, config in models_to_tune.items():
    print(f"\n{'=' * 60}")
    print(f"Tuning: {model_name}")
    print(f"{'=' * 60}")
    
    n_combos = 1
    for v in config['param_grid'].values():
        n_combos *= len(v)
    print(f"  Grid: {n_combos} combinations x 3-fold CV = {n_combos * 3} fits")
    
    start_time = time.time()
    
    gs = GridSearchCV(
        estimator=config['model'],
        param_grid=config['param_grid'],
        cv=3,
        scoring='r2',
        n_jobs=-1,
        verbose=1,
        return_train_score=True
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
    
    print(f"\n  [OK] Tuned in {elapsed:.1f}s")
    print(f"\n  Best Parameters:")
    for param, value in gs.best_params_.items():
        print(f"    {param}: {value}")
    print(f"\n  Log-space performance:")
    print(f"    CV R² (log):         {cv_score:.4f}")
    print(f"    Train R² (log):      {train_r2_log:.4f}")
    print(f"    Test R² (log):       {test_r2_log:.4f}")
    print(f"\n  Original-scale performance:")
    print(f"    Train R² (original): {train_r2:.4f}")
    print(f"    Test R² (original):  {test_r2:.4f}")
    print(f"    RMSE (original):     INR {rmse:,.0f}")
    print(f"    MAE (original):      INR {mae:,.0f}")
    
    # Save best model
    model_path = f'ml_ready/models/{model_name.lower().replace(" ", "_")}.pkl'
    joblib.dump(gs.best_estimator_, model_path)
    best_models[model_name] = gs.best_estimator_
    print(f"\n  Saved: {model_path}")
    
    tuning_results.append({
        'Model': model_name,
        'Best Params': gs.best_params_,
        'CV R² (log)': cv_score,
        'Test R² (log)': test_r2_log,
        'Test R² (orig)': test_r2,
        'RMSE (orig)': rmse,
        'MAE (orig)': mae,
        'Train R² (orig)': train_r2,
        'Tuning Time (s)': round(elapsed, 1)
    })
    
    # Save full GridSearchCV results for analysis
    results_df_path = f'ml_ready/models/{model_name.lower().replace(" ", "_")}_gs_results.json'
    cv_results = {
        'params': [str(p) for p in gs.cv_results_['params']],
        'mean_test_score': [round(s, 4) for s in gs.cv_results_['mean_test_score']],
        'std_test_score': [round(s, 4) for s in gs.cv_results_['std_test_score']],
        'mean_train_score': [round(s, 4) for s in gs.cv_results_['mean_train_score']],
        'rank_test_score': [int(s) for s in gs.cv_results_['rank_test_score']]
    }
    with open(results_df_path, 'w') as f:
        json.dump(cv_results, f, indent=2)

# =========================================================================
# Summary
# =========================================================================
print(f"\n{'=' * 70}")
print("TUNING SUMMARY")
print(f"{'=' * 70}")
print(f"{'Model':<22} {'Test R² (orig)':<16} {'RMSE':<14} {'MAE':<14} {'Time (s)':<10}")
print("-" * 76)

for r in sorted(tuning_results, key=lambda x: x['Test R² (orig)'], reverse=True):
    print(f"{r['Model']:<22} {r['Test R² (orig)']:<16.4f} INR {r['RMSE (orig)']:<10,.0f} INR {r['MAE (orig)']:<10,.0f} {r['Tuning Time (s)']:<10.1f}")

print(f"\n{'=' * 70}")
print("BEST PARAMETERS (for use in training)")
print(f"{'=' * 70}")
for r in tuning_results:
    print(f"\n{r['Model']}:")
    for param, value in r['Best Params'].items():
        print(f"  {param}: {value}")

print(f"\nAll tuned models saved to ml_ready/models/")
print("Done!")
