import pandas as pd

df = pd.read_csv("data/Cleaned_Car_data.csv", index_col=0)
logger.info("dtypes")
logger.info("dtypes_table", dtypes=str(df.dtypes))
logger.info("")

# Check for non-numeric Price
bad_price = df[pd.to_numeric(df["Price"], errors="coerce").isna()]
logger.info("non_numeric_price_rows", count=len(bad_price))
if len(bad_price) > 0:
    print(bad_price[["name", "Price"]].head(10))
    print()

# Check for non-numeric year
bad_year = df[pd.to_numeric(df["year"], errors="coerce").isna()]
logger.info("non_numeric_year_rows", count=len(bad_year))
if len(bad_year) > 0:
    print(bad_year[["name", "year"]].head(10))
    print()

# Check for non-numeric kms_driven
bad_kms = df[pd.to_numeric(df["kms_driven"], errors="coerce").isna()]
logger.info("non_numeric_kms_rows", count=len(bad_kms))
if len(bad_kms) > 0:
    print(bad_kms[["name", "kms_driven"]].head(10))

# Ensure proper types
logger.info("sample_problem_rows")
logger.info("sample_rows", data=str(df.iloc[1590:1600]))
