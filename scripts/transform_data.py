import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="shopkart",
    user="postgres"
)

cursor = conn.cursor()

transform_query = """
select order_date, sum(total_amount) as total_revenue, count(order_id) as total_orders, avg(total_amount) as average_order_value from orders group by order_date;
"""

cursor.execute(transform_query)

rows = cursor.fetchall()

print(f"Transformed {len(rows)} daily records.")
for row in rows:
    print(row)