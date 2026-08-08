from pathlib import Path
import pandas as pd

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load data
file_path = BASE_DIR / "data" / "orders.csv"
df = pd.read_csv(file_path)

print("=" * 60)
print("SHOPKART BUSINESS REPORT")
print("=" * 60)

# 1. Total Revenue
total_revenue = df["total_amount"].sum()
print(f"\n💰 Total Revenue: ₹{total_revenue:,.2f}")

# 2. Total Orders
print(f"\n📦 Total Orders: {len(df)}")

# 3. Top 5 Products
print("\n🏆 Top 5 Products")
print(df.groupby("product")["quantity"].sum().sort_values(ascending=False).head())

# 4. Revenue by City
print("\n🏙 Revenue by City")
print(df.groupby("city")["total_amount"].sum().sort_values(ascending=False))

# 5. Payment Methods
print("\n💳 Payment Methods")
print(df["payment_method"].value_counts())

# 6. Average Order Value
avg_order = df["total_amount"].mean()
print(f"\n🛒 Average Order Value: ₹{avg_order:,.2f}")

print("\n" + "=" * 60)