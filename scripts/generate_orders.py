from pathlib import Path
import random

import pandas as pd
from faker import Faker

# -----------------------------
# Configuration
# -----------------------------
fake = Faker("en_IN")
random.seed(42)

PRODUCTS = {
    "Laptop": ("Electronics", 65000),
    "Phone": ("Electronics", 25000),
    "Headphones": ("Electronics", 3000),
    "Shoes": ("Fashion", 2500),
    "T-Shirt": ("Fashion", 800),
    "Watch": ("Accessories", 5000),
    "Book": ("Books", 500),
    "Desk": ("Furniture", 7000),
    "Chair": ("Furniture", 4000),
    "Bottle": ("Home", 600),
}

PRODUCT_WEIGHTS = {
    "Laptop": 10,
    "Phone": 30,
    "Headphones": 20,
    "Shoes": 15,
    "T-Shirt": 10,
    "Watch": 5,
    "Book": 3,
    "Desk": 2,
    "Chair": 3,
    "Bottle": 2,
}

CITIES = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Pune",
    "Ahmedabad",
    "Chennai",
    "Kolkata",
]

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Cash on Delivery",
    "Net Banking",
]


def generate_orders(num_orders=10000):
    """Generate fake e-commerce order data."""
    orders = []

    for order_id in range(1, num_orders + 1):
        product = random.choices(list(PRODUCT_WEIGHTS.keys()), weights=list(PRODUCT_WEIGHTS.values()), k=1)[0]
        category, unit_price = PRODUCTS[product]
        quantity = random.randint(1, 5)

        orders.append({
            "order_id": order_id,
            "customer_id": random.randint(1000, 9999),
            "customer_name": fake.name(),
            "product": product,
            "category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": quantity * unit_price,
            "city": random.choice(CITIES),
            "payment_method": random.choice(PAYMENT_METHODS),
            "order_date": fake.date_between(start_date="-365d", end_date="today"),
            "delivery_days": random.randint(1, 7),
        })

    return pd.DataFrame(orders)


def main():
    # Generate DataFrame
    df = generate_orders(10000)

    # Project root (one level above the scripts folder)
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Create data directory if it doesn't exist
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Output file
    output_file = DATA_DIR / "orders.csv"

    # Save CSV
    df.to_csv(output_file, index=False)

    print("=" * 60)
    print("✅ ShopKart Orders Generated Successfully")
    print("=" * 60)
    print(df.head())
    print()
    print(f"Total Orders : {len(df)}")
    print(f"Saved To     : {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()