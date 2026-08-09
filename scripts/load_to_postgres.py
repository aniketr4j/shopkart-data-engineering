import pandas as pd  # type: ignore[import-not-found]
import psycopg2  # type: ignore[import-not-found]


# --------------------------------------------------
# 1. Load CSV
# --------------------------------------------------

df = pd.read_csv("data/orders.csv")

print(f"Loaded {len(df)} orders from CSV.")


# --------------------------------------------------
# 2. Connect to PostgreSQL
# --------------------------------------------------

conn = psycopg2.connect(
    host="localhost",
    database="shopkart",
    user="postgres"
)

cursor = conn.cursor()


# --------------------------------------------------
# 3. Create orders table
# --------------------------------------------------

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


# --------------------------------------------------
# 4. Create daily_sales table
# --------------------------------------------------

create_sales_query = """
CREATE TABLE IF NOT EXISTS daily_sales (
    order_date DATE,
    total_orders INTEGER,
    total_revenue NUMERIC(10, 2),
    average_order_value NUMERIC(10, 2)
);
"""

cursor.execute(create_sales_query)


# --------------------------------------------------
# 5. Create city_revenue table
# --------------------------------------------------

create_city_revenue_query = """
CREATE TABLE IF NOT EXISTS city_revenue (
    city VARCHAR(50),
    revenue NUMERIC(12, 2)
);
"""

cursor.execute(create_city_revenue_query)


# --------------------------------------------------
# 6. Insert orders query
# --------------------------------------------------

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
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict (order_id) do nothing;
"""


# --------------------------------------------------
# 7. Daily sales transformation
# --------------------------------------------------

insert_sales_query = """
INSERT INTO daily_sales (
    order_date,
    total_orders,
    total_revenue,
    average_order_value
)
SELECT
    order_date,
    COUNT(*) AS total_orders,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_order_value
FROM orders
GROUP BY order_date;
"""


# --------------------------------------------------
# 8. City revenue transformation
# --------------------------------------------------

insert_city_revenue_query = """
INSERT INTO city_revenue (
    city,
    revenue
)
SELECT
    city,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY city
ORDER BY revenue DESC;
"""


# --------------------------------------------------
# 9. Convert DataFrame rows
# --------------------------------------------------

rows = []

for _, row in df.iterrows():

    values = [
        value.item() if hasattr(value, "item") else value
        for value in row
    ]

    rows.append(tuple(values))


# --------------------------------------------------
# 10. Clear previous data
# --------------------------------------------------

cursor.execute("TRUNCATE TABLE daily_sales;")
cursor.execute("TRUNCATE TABLE city_revenue;")


# --------------------------------------------------
# 11. Load orders
# --------------------------------------------------

cursor.executemany(insert_query, rows)


# --------------------------------------------------
# 12. Create daily sales analytics
# --------------------------------------------------

cursor.execute(insert_sales_query)


# --------------------------------------------------
# 13. Create city revenue analytics
# --------------------------------------------------

cursor.execute(insert_city_revenue_query)


# --------------------------------------------------
# 14. Commit changes
# --------------------------------------------------

conn.commit()


# --------------------------------------------------
# 15. Close connection
# --------------------------------------------------

cursor.close()
conn.close()


print("Orders and analytics tables loaded successfully!")

