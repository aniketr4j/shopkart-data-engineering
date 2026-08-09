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

city_revenue_query = """
select city, sum(total_amount) as total_revenue from orders group by city order by total_revenue desc;
"""

cursor.execute(city_revenue_query)


city_rows = cursor.fetchall()

print(f"Retrieved {len(city_rows)} city revenue records.")
for row in city_rows:
    print(row)