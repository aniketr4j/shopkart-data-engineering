from pathlib import Path
import pandas as pd

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Read CSV
file_path = BASE_DIR / "data" / "orders.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("SHOPKART DATA QUALITY REPORT")
print("=" * 60)

print("\n1. First 5 Rows")
print(df.head())

print("\n2. Dataset Shape")
print(df.shape)

print("\n3. Column Names")
print(df.columns.tolist())

print("\n4. Data Types")
print(df.dtypes)

print("\n5. Missing Values")
print(df.isnull().sum())

print("\n6. Duplicate Rows")
print(df.duplicated().sum())

print("\n7. Summary Statistics")
print(df.describe())

print("\n--- Total Amount Check ---")
df["calculated_total_amount"] = df["quantity"] * df["unit_price"]
mismatched_total_amount = (df["total_amount"] != df["calculated_total_amount"]).sum()

print(f"Number of mismatched total amounts: {mismatched_total_amount}")
print("\n--- Quantity Validation ---")
invalid_quantity = df[(df["quantity"] < 1) | (df["quantity"] > 5)]
print(f"Number of invalid quantities: {len(invalid_quantity)}")

print("\n --- Price Validation ---")
invalid_price = df[df["unit_price"] <= 0]
print(f"Number of invalid prices: {len(invalid_price)}")

print("\n --- Delivery Validation ---")
invalid_delivery = df[(df["delivery_days"]< 1) | (df["delivery_days"] > 7)]
print(f"Number of invalid delivery days: {len(invalid_delivery)}")

print("=" * 60)