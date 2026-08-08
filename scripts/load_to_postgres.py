import pandas as pd  # type: ignore[import-not-found]
import psycopg2  # type: ignore[import-not-found]

df = pd.read_csv("data/orders.csv")

print(f"Loaded {len(df)} orders from CSV.")

conn = psycopg2.connect(
    host="localhost",
    database="shopkart",
    user="postgres"
)

cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER,
    customer_id INTEGER,
    customer_name VARCHAR(100),
    product VARCHAR(50),
    category VARCHAR(50),
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),
    city VARCHAR(50),
    payment_method VARCHAR(50),
    order_date DATE,
    delivery_days INTEGER
);
"""
cursor.execute(create_table_query)

insert_query = """
INSERT INTO orders (
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
    
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
first_row = df.iloc[0]

# values = [
#     value.item() if hasattr(value, "item") else value
#     for value in first_row
# ]
rows = []

for _, row in df.iterrows():
    values = [
        value.item() if hasattr(value, "item") else value
        for value in row
    ]
    rows.append(tuple(values))
cursor.executemany(insert_query, rows)

conn.commit()

cursor.close()
conn.close()

print("Orders table created successfully!")