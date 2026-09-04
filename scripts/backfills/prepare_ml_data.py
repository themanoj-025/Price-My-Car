"""
Car Price Prediction - Data Preprocessing for ML
==================================================
This script prepares the Cleaned_Car_data.csv for ML algorithms:
- Removes duplicates
- Feature engineering (car_age, brand extraction)
- Encodes categorical variables (fuel_type, company)
- Scales numerical features
- Splits into train/test sets
- Saves processed data as .npy files and a CSV
"""

import os
import warnings

import joblib
import numpy as np
import pandas as pd
import structlog
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

logger = structlog.get_logger("prepare_ml_data")

logger.info("car_price_prediction_data_preparation")

# -- 1. Load Data ----------------------------------------------------------
df = pd.read_csv("data/Cleaned_Car_data.csv", index_col=0)
logger.info("dataset_loaded", rows=df.shape[0], cols=df.shape[1], columns=df.columns.tolist())

# -- 2. Remove Duplicates --------------------------------------------------
initial_count = len(df)
df = df.drop_duplicates().reset_index(drop=True)
dupes_removed = initial_count - len(df)
logger.info("duplicates_removed", removed=dupes_removed, remaining=len(df))

# -- 3. Feature Engineering ------------------------------------------------
CURRENT_YEAR = 2025
df["car_age"] = CURRENT_YEAR - df["year"]

# Simplify fuel_type: group rare categories (CNG, LPG, Electric -> Alternative)
df["fuel_type_simple"] = df["fuel_type"].replace(
    {"CNG": "Alternative", "LPG": "Alternative", "Electric": "Alternative"}
)

# -- 4. Handle Outliers (kms_driven) --------------------------------------
kms_upper = df["kms_driven"].quantile(0.99)
kms_outliers = (df["kms_driven"] > kms_upper).sum()
df["kms_driven"] = df["kms_driven"].clip(upper=kms_upper)
logger.info("outliers_capped", column="kms_driven", count=kms_outliers, upper=f"{kms_upper:,.0f}")

# -- 5. Drop unnecessary columns ------------------------------------------
df_ml = df.drop(columns=["name", "year", "fuel_type"])

features = [c for c in df_ml.columns if c != "Price"]
logger.info("features_engineered", features=features)

# -- 6. Log-Transform Target (handle heavy right skew in Price) ---------------
y_original = df_ml["Price"].copy()
y_log = np.log1p(df_ml["Price"])  # log(1 + price) — handles zero values

logger.info("log_transformed_price", original_skew=round(y_original.skew(), 2), log_skew=round(y_log.skew(), 2), original_range=f"Rs.{y_original.min():,.0f} - Rs.{y_original.max():,.0f}", log_range=f"{y_log.min():.4f} - {y_log.max():.4f}")

# -- 7. Train/Test Split --------------------------------------------------
X = df_ml.drop(columns=["Price"])

X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.2, random_state=42)

logger.info("train_test_split", x_train_shape=str(X_train.shape), y_train_shape=str(y_train.shape), x_test_shape=str(X_test.shape), y_test_shape=str(y_test.shape))

# -- 8. Preprocessing Pipeline --------------------------------------------
categorical_features = ["company", "fuel_type_simple"]
numerical_features = ["car_age", "kms_driven"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            categorical_features,
        ),
    ]
)

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(
    categorical_features
)
all_feature_names = numerical_features + list(cat_feature_names)

logger.info("preprocessing_complete")
logger.info("x_train_processed", shape=str(X_train_processed.shape))
logger.info("x_test_processed", shape=str(X_test_processed.shape))
logger.info("feature_count", count=len(all_feature_names))

# -- 9. Save Processed Data -----------------------------------------------
os.makedirs("ml_ready", exist_ok=True)

np.save("ml_ready/X_train.npy", X_train_processed)
np.save("ml_ready/X_test.npy", X_test_processed)
np.save("ml_ready/y_train.npy", y_train.values)
np.save("ml_ready/y_test.npy", y_test.values)
np.save("ml_ready/feature_names.npy", np.array(all_feature_names, dtype=object))

train_df = pd.DataFrame(X_train_processed, columns=all_feature_names)
train_df["Price"] = y_train.values
train_df.to_csv("ml_ready/train_data.csv", index=False)

test_df = pd.DataFrame(X_test_processed, columns=all_feature_names)
test_df["Price"] = y_test.values
test_df.to_csv("ml_ready/test_data.csv", index=False)

joblib.dump(preprocessor, "ml_ready/preprocessor.pkl")
joblib.dump(all_feature_names, "ml_ready/feature_names.pkl")

# Also save original (untransformed) y for reference / EDA
y_original_train, y_original_test = train_test_split(y_original, test_size=0.2, random_state=42)
np.save("ml_ready/y_train_original.npy", y_original_train.values)
np.save("ml_ready/y_test_original.npy", y_original_test.values)
logger.info("saved_original_price")

logger.info("files_saved", dir="ml_ready/", x_train_mb=round(X_train_processed.nbytes / 1e6, 1), files=["X_train.npy", "X_test.npy", "y_train.npy", "y_test.npy", "y_train_original.npy", "y_test_original.npy", "feature_names.npy", "train_data.csv", "test_data.csv"])
logger.info("saved_preprocessor")
logger.info("saved_feature_names")

# -- 10. Summary -----------------------------------------------------------
logger.info("data_preparation_summary")
logger.info("original_rows", count=initial_count)
logger.info("duplicates_removed", count=dupes_removed)
logger.info("final_rows", count=len(df))
logger.info("features", count=len(all_feature_names))
logger.info("train_samples", count=len(y_train))
logger.info("test_samples", count=len(y_test))
logger.info("target", description="Price log1p-transformed regression")
logger.info("skewness", original=round(y_original.skew(), 2), log=round(y_log.skew(), 2))
logger.info("predict_hint")
logger.info("ml_algorithms_ready")
logger.info("linear_models")
logger.info("tree_models")
logger.info("neural_networks")

# -- 11. Sanity Check -----------------------------------------------------
logger.info("quick_validation")
logger.info("x_train_mean", values=str(X_train_processed.mean(axis=0)[:5].round(3)))
logger.info("x_train_std", values=str(X_train_processed.std(axis=0)[:5].round(3)))
logger.info("y_train_log_range", min=round(y_train.min(), 4), max=round(y_train.max(), 4))
logger.info("y_train_log_mean", mean=round(y_train.mean(), 4))
logger.info("inverse_check", expm1_mean=round(float(np.expm1(y_train.mean())), 0))
logger.info("missing_values", count=int(np.isnan(X_train_processed).sum()))
logger.info("data_preparation_complete")
