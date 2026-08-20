import pandas as pd
import psycopg2
from data_quality_check import validate_data
import logging
from pathlib import Path


# --------------------------------------------------
# Logging setup
# --------------------------------------------------

logs_dir = Path("logs")
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename="logs/shopkart_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Pipeline started.")


# --------------------------------------------------
# 1. Read incoming orders
# --------------------------------------------------

df = pd.read_csv("data/new_orders.csv")

print(f"Received {len(df)} orders from CSV.")
logging.info(f"Received {len(df)} orders from CSV.")


# --------------------------------------------------
# 2. Connect to PostgreSQL
# --------------------------------------------------

conn = psycopg2.connect(
    host="localhost",
    database="shopkart",
    user="postgres"
)

cursor = conn.cursor()

logging.info("Connected to PostgreSQL database.")


# --------------------------------------------------
# 3. Get existing order IDs from PostgreSQL
# --------------------------------------------------

cursor.execute("SELECT order_id FROM orders;")

existing_ids = {
    row[0]
    for row in cursor.fetchall()
}

existing_in_batch = df["order_id"].isin(existing_ids).sum()

print(f"Existing orders in database: {len(existing_ids)}")
print(f"Already existing in this batch: {existing_in_batch}")

logging.info(f"Existing orders in database: {len(existing_ids)}")
logging.info(f"Already existing in this batch: {existing_in_batch}")


# --------------------------------------------------
# 4. Keep only genuinely NEW orders
# --------------------------------------------------

new_df = df[
    ~df["order_id"].isin(existing_ids)
].copy()

print(f"New orders to process: {len(new_df)}")
logging.info(f"New orders to process: {len(new_df)}")


# --------------------------------------------------
# 5. Validate only NEW orders
# --------------------------------------------------

valid_df, invalid_df = validate_data(new_df)

print(f"Valid new orders: {len(valid_df)}")
print(f"Invalid new orders: {len(invalid_df)}")

logging.info(f"Valid new orders: {len(valid_df)}")
logging.info(f"Invalid new orders: {len(invalid_df)}")


# --------------------------------------------------
# 6. Save rejected orders
# --------------------------------------------------

if len(invalid_df) > 0:

    invalid_df.to_csv(
        "data/rejected_orders.csv",
        index=False
    )

    print(
        "Rejected orders saved to "
        "data/rejected_orders.csv"
    )

    logging.warning(
        f"{len(invalid_df)} invalid orders rejected."
    )

    logging.info(
        "Rejected orders saved to data/rejected_orders.csv"
    )


# --------------------------------------------------
# 7. Insert only VALID NEW orders
# --------------------------------------------------

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
)
VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s
)
ON CONFLICT (order_id) DO NOTHING;
"""


rows = []

for _, row in valid_df.iterrows():

    values = [
        value.item() if hasattr(value, "item") else value
        for value in row
    ]

    rows.append(tuple(values))


# --------------------------------------------------
# 8. Load valid records
# --------------------------------------------------

load_success = False

if rows:

    try:

        cursor.executemany(
            insert_query,
            rows
        )

        print(
            f"Loaded {len(rows)} valid new orders "
            "into PostgreSQL."
        )

        logging.info(
            f"Loaded {len(rows)} valid new orders into PostgreSQL."
        )


        # --------------------------------------------------
        # 9. Get affected dates and cities
        # --------------------------------------------------

        affected_dates = valid_df["order_date"].unique()
        affected_cities = valid_df["city"].unique()


        # --------------------------------------------------
        # 10. Update daily_sales
        # --------------------------------------------------

        update_daily_sales_query = """
        INSERT INTO daily_sales (
            order_date,
            total_orders,
            total_revenue,
            average_order_value
        )
        SELECT
            order_date,
            COUNT(*),
            SUM(total_amount),
            AVG(total_amount)
        FROM orders
        WHERE order_date = %s
        GROUP BY order_date
        ON CONFLICT (order_date)
        DO UPDATE SET
            total_orders = EXCLUDED.total_orders,
            total_revenue = EXCLUDED.total_revenue,
            average_order_value = EXCLUDED.average_order_value;
        """

        for order_date in affected_dates:

            cursor.execute(
                update_daily_sales_query,
                (order_date,)
            )

        print("Daily sales updated successfully.")
        logging.info("Daily sales updated successfully.")


        # --------------------------------------------------
        # 11. Update city_revenue
        # --------------------------------------------------

        update_city_revenue_query = """
        INSERT INTO city_revenue (
            city,
            revenue
        )
        SELECT
            city,
            SUM(total_amount)
        FROM orders
        WHERE city = %s
        GROUP BY city
        ON CONFLICT (city)
        DO UPDATE SET
            revenue = EXCLUDED.revenue;
        """

        for city in affected_cities:

            cursor.execute(
                update_city_revenue_query,
                (city,)
            )

        print("City revenue updated successfully.")
        logging.info("City revenue updated successfully.")


        # --------------------------------------------------
        # 12. Commit transaction
        # --------------------------------------------------

        conn.commit()

        load_success = True

        logging.info(
            "Transaction committed successfully."
        )


    except Exception as e:

        conn.rollback()

        print(
            "Error occurred while loading data:",
            e
        )

        print(
            "Rolling back changes to maintain data integrity."
        )

        logging.error(
            f"Error occurred during pipeline: {e}"
        )

        logging.error(
            "Transaction rolled back."
        )


else:

    print("No valid new orders to load.")

    logging.info(
        "No valid new orders to load."
    )


# --------------------------------------------------
# 13. Close connection
# --------------------------------------------------

cursor.close()
conn.close()

logging.info("PostgreSQL connection closed.")


# --------------------------------------------------
# 14. Pipeline Summary
# --------------------------------------------------

print()
print("=" * 60)
print("SHOPKART INCREMENTAL LOAD SUMMARY")
print("=" * 60)

print(f"Records received        : {len(df)}")
print(f"Already existing        : {existing_in_batch}")
print(f"New records             : {len(new_df)}")
print(f"Valid records           : {len(valid_df)}")
print(f"Rejected records        : {len(invalid_df)}")
print(f"Records loaded          : {len(rows)}")

print("=" * 60)


# --------------------------------------------------
# 15. Final pipeline status
# --------------------------------------------------

if load_success:

    print("Incremental load completed successfully!")

    logging.info(
        "Incremental load completed successfully."
    )

elif len(rows) == 0:

    print(
        "Incremental load completed. "
        "No valid records to load."
    )

    logging.info(
        "Incremental load completed. "
        "No valid records to load."
    )

else:

    print(
        "Incremental load failed. "
        "Changes were rolled back."
    )

    logging.error(
        "Incremental load failed. "
        "Changes were rolled back."
    )