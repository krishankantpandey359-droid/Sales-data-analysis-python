from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {"Date", "Product", "Region", "Sales", "Profit"}


def load_sales_data(data_path):
    """Load sales data and reject malformed records before calculating totals."""
    frame = pd.read_csv(data_path)
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}"
        )
    if frame.empty:
        raise ValueError("Dataset contains no sales records.")

    for column in ("Product", "Region"):
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Dataset contains missing {column} values.")

    try:
        frame["Date"] = pd.to_datetime(frame["Date"], errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Dataset contains invalid Date values.") from exc

    for column in ("Sales", "Profit"):
        try:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Dataset contains non-numeric {column} values.") from exc
        if frame[column].isna().any() or not frame[column].map(pd.notna).all():
            raise ValueError(f"Dataset contains missing {column} values.")
        if not frame[column].map(lambda value: abs(value) != float("inf")).all():
            raise ValueError(f"Dataset contains non-finite {column} values.")

    return frame


def main():
    # Load the dataset from the same directory as this script.
    data_path = Path(__file__).resolve().with_name("sales_data.csv")
    df = load_sales_data(data_path)

    # Overall performance
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    print(f"Total Sales: {total_sales:,.2f}")
    print(f"Total Profit: {total_profit:,.2f}")

    # Sales breakdowns
    region_sales = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    product_sales = df.groupby("Product")["Sales"].sum().sort_values(ascending=False)

    print("\\nSales by Region:")
    print(region_sales.to_string())

    print("\\nSales by Product:")
    print(product_sales.to_string())

    # Visualize sales by region
    ax = region_sales.plot(kind="bar", title="Sales by Region", rot=0)
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
