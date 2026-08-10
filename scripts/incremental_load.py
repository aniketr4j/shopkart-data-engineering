import pandas as pd
import psycopg2

df = pd.read_csv("data/new_orders.csv")

print(f"Loaded {len(df)} new orders from CSV.")

conn = psycopg2.connect(
    host="localhost",
    database="shopkart",
    user="postgres"
)

cursor = conn.cursor()

insert_query = """
INSERT INTO orders(
    order_id,
    customer_id,
    customer_name,
    product,
    category,
    quantity,
    unit_price,
    total_amount,
    city,
    payment_method,
    order_date,
    delivery_days
) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict (order_id) do nothing;
"""

rows = []

for _, row in df.iterrows():
    values = [
        value.item() if hasattr(value, "item") else value
        for value in row
    ]
    rows.append(tuple(values))

cursor.executemany(insert_query, rows)
conn.commit()
conn.close()

print("Incremental load completed successfully!")