from pathlib import Path
import pandas as pd


def validate_data(df):

    valid_rows = []
    invalid_rows = []

    for _, row in df.iterrows():

        errors = []

        if row["quantity"] < 1 or row["quantity"] > 5:
            errors.append("Invalid quantity")

        if row["unit_price"] <= 0:
            errors.append("Invalid unit price")

        if row["delivery_days"] < 1 or row["delivery_days"] > 7:
            errors.append("Invalid delivery days")

        calculated_total_amount = (
            row["quantity"] * row["unit_price"]
        )

        if abs(
            row["total_amount"] - calculated_total_amount
        ) > 0.01:
            errors.append("Mismatched total amount")

        if errors:
            row["error_reason"] = "; ".join(errors)
            invalid_rows.append(row)
        else:
            valid_rows.append(row)

    valid_df = pd.DataFrame(valid_rows)
    invalid_df = pd.DataFrame(invalid_rows)

    return valid_df, invalid_df


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent

    file_path = BASE_DIR / "data" / "new_orders.csv"

    df = pd.read_csv(file_path)

    valid_df, invalid_df = validate_data(df)

    print("=" * 60)
    print("SHOPKART DATA QUALITY REPORT")
    print("=" * 60)

    print(f"Number of valid rows: {len(valid_df)}")
    print(f"Number of invalid rows: {len(invalid_df)}")

    if len(invalid_df) > 0:

        rejected_file = (
            BASE_DIR / "data" / "rejected_orders.csv"
        )

        invalid_df.to_csv(
            rejected_file,
            index=False
        )

        print(
            f"Rejected records saved to: {rejected_file}"
        )

    else:
        print("No invalid records found.")