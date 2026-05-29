import pandas as pd
import numpy as np

df = pd.read_csv('Cleaned_Car_data.csv', index_col=0)
print("Dtypes:")
print(df.dtypes)
print()

# Check for non-numeric Price
bad_price = df[pd.to_numeric(df['Price'], errors='coerce').isna()]
print("Non-numeric Price rows:", len(bad_price))
if len(bad_price) > 0:
    print(bad_price[['name', 'Price']].head(10))
    print()

# Check for non-numeric year
bad_year = df[pd.to_numeric(df['year'], errors='coerce').isna()]
print("Non-numeric year rows:", len(bad_year))
if len(bad_year) > 0:
    print(bad_year[['name', 'year']].head(10))
    print()

# Check for non-numeric kms_driven
bad_kms = df[pd.to_numeric(df['kms_driven'], errors='coerce').isna()]
print("Non-numeric kms_driven rows:", len(bad_kms))
if len(bad_kms) > 0:
    print(bad_kms[['name', 'kms_driven']].head(10))
    
# Ensure proper types
print("Sample rows around where issues might be:")
print(df.iloc[1590:1600])
