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

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import warnings
import os
import joblib

warnings.filterwarnings('ignore')

print("=" * 60)
print("CAR PRICE PREDICTION - ML DATA PREPARATION")
print("=" * 60)

# -- 1. Load Data ----------------------------------------------------------
df = pd.read_csv('Cleaned_Car_data.csv', index_col=0)
print(f"\n[1] Loaded dataset: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"    Columns: {df.columns.tolist()}")

# -- 2. Remove Duplicates --------------------------------------------------
initial_count = len(df)
df = df.drop_duplicates().reset_index(drop=True)
dupes_removed = initial_count - len(df)
print(f"\n[2] Removed {dupes_removed} duplicate rows ({len(df)} remaining)")

# -- 3. Feature Engineering ------------------------------------------------
CURRENT_YEAR = 2025
df['car_age'] = CURRENT_YEAR - df['year']

# Simplify fuel_type: group rare categories (CNG, LPG, Electric -> Alternative)
df['fuel_type_simple'] = df['fuel_type'].replace({
    'CNG': 'Alternative',
    'LPG': 'Alternative',
    'Electric': 'Alternative'
})

# -- 4. Handle Outliers (kms_driven) --------------------------------------
kms_upper = df['kms_driven'].quantile(0.99)
kms_outliers = (df['kms_driven'] > kms_upper).sum()
df['kms_driven'] = df['kms_driven'].clip(upper=kms_upper)
print(f"\n[4] Capped {kms_outliers} kms_driven outliers at 99th percentile ({kms_upper:,.0f})")

# -- 5. Drop unnecessary columns ------------------------------------------
df_ml = df.drop(columns=['name', 'year', 'fuel_type'])

features = [c for c in df_ml.columns if c != 'Price']
print(f"\n[5] Features after engineering: {features}")

# -- 6. Log-Transform Target (handle heavy right skew in Price) ---------------
y_original = df_ml['Price'].copy()
y_log = np.log1p(df_ml['Price'])  # log(1 + price) — handles zero values

print(f"\n[6] Log-transformed Price:")
print(f"    Original skewness: {y_original.skew():.2f}")
print(f"    Log-transformed skewness: {y_log.skew():.2f}")
print(f"    Original range: Rs.{y_original.min():,.0f} - Rs.{y_original.max():,.0f}")
print(f"    Log range: {y_log.min():.4f} – {y_log.max():.4f}")

# -- 7. Train/Test Split --------------------------------------------------
X = df_ml.drop(columns=['Price'])

X_train, X_test, y_train, y_test = train_test_split(
    X, y_log, test_size=0.2, random_state=42
)

print(f"\n[7] Train/test split:")
print(f"    X_train: {X_train.shape}, y_train: {y_train.shape}")
print(f"    X_test:  {X_test.shape}, y_test:  {y_test.shape}")

# -- 8. Preprocessing Pipeline --------------------------------------------
categorical_features = ['company', 'fuel_type_simple']
numerical_features = ['car_age', 'kms_driven']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ]
)

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
all_feature_names = numerical_features + list(cat_feature_names)

print(f"\n[8] Preprocessing complete:")
print(f"    X_train processed: {X_train_processed.shape}")
print(f"    X_test processed:  {X_test_processed.shape}")
print(f"    Feature count:     {len(all_feature_names)}")

# -- 9. Save Processed Data -----------------------------------------------
os.makedirs('ml_ready', exist_ok=True)

np.save('ml_ready/X_train.npy', X_train_processed)
np.save('ml_ready/X_test.npy', X_test_processed)
np.save('ml_ready/y_train.npy', y_train.values)
np.save('ml_ready/y_test.npy', y_test.values)
np.save('ml_ready/feature_names.npy', np.array(all_feature_names, dtype=object))

train_df = pd.DataFrame(X_train_processed, columns=all_feature_names)
train_df['Price'] = y_train.values
train_df.to_csv('ml_ready/train_data.csv', index=False)

test_df = pd.DataFrame(X_test_processed, columns=all_feature_names)
test_df['Price'] = y_test.values
test_df.to_csv('ml_ready/test_data.csv', index=False)

joblib.dump(preprocessor, 'ml_ready/preprocessor.pkl')
joblib.dump(all_feature_names, 'ml_ready/feature_names.pkl')

# Also save original (untransformed) y for reference / EDA
y_original_train, y_original_test = train_test_split(
    y_original, test_size=0.2, random_state=42
)
np.save('ml_ready/y_train_original.npy', y_original_train.values)
np.save('ml_ready/y_test_original.npy', y_original_test.values)
print(f"    Also saved original (untransformed) Price to y_train_original.npy / y_test_original.npy")

print(f"\n[9] Saved to 'ml_ready/' folder:")
print(f"    |-- X_train.npy        ({X_train_processed.nbytes/1e6:.1f} MB)")
print(f"    |-- X_test.npy")
print(f"    |-- y_train.npy        (log1p-transformed)")
print(f"    |-- y_test.npy         (log1p-transformed)")
print(f"    |-- y_train_original.npy (original Price for reference)")
print(f"    |-- y_test_original.npy")
print(f"    |-- feature_names.npy")
print(f"    |-- train_data.csv")
print(f"    |-- test_data.csv")
print(f"    |-- preprocessor.pkl")
print(f"    |-- feature_names.pkl")

# -- 10. Summary -----------------------------------------------------------
print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
print(f"  Original rows:      {initial_count}")
print(f"  Duplicates removed: {dupes_removed}")
print(f"  Final rows:         {len(df)}")
print(f"  Features:           {len(all_feature_names)}")
print(f"  Train samples:      {len(y_train)}")
print(f"  Test samples:       {len(y_test)}")
print(f"  Target:             Price (log1p-transformed regression)")
print(f"  Original skewness:  {y_original.skew():.2f} -> log skewness: {y_log.skew():.2f}")
print(f"")
print(f"  Predict with:       np.expm1(prediction) to get original INR price")
print(f"")
print(f"  Ready for ML algorithms like:")
print(f"    - Linear Regression / Ridge / Lasso")
print(f"    - Random Forest / Gradient Boosting / XGBoost")
print(f"    - Neural Networks")
print(f"{'=' * 60}")

# -- 11. Sanity Check -----------------------------------------------------
print(f"\n[11] Quick validation:")
print(f"    X_train mean (should be ~0): {X_train_processed.mean(axis=0)[:5].round(3)}")
print(f"    X_train std  (should be ~1): {X_train_processed.std(axis=0)[:5].round(3)}")
print(f"    y_train (log) range: {y_train.min():.4f} - {y_train.max():.4f}")
print(f"    y_train (log) mean:  {y_train.mean():.4f}")
print(f"    Inverse check: expm1({y_train.mean():.4f}) = Rs.{np.expm1(y_train.mean()):,.0f} (original price scale)")
print(f"    Missing values in processed data: {np.isnan(X_train_processed).sum()}")
print(f"\nDone! ML-ready data successfully prepared.")
