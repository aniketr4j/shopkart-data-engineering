import pandas as pd

df = pd.read_csv("data/orders.csv")

# print(df["product"].value_counts())

print("\nProduct Percentage:")
print(df["product"].value_counts(normalize=True) * 100)