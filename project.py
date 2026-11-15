from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = Path(__file__).resolve().with_name("sales_data.csv")
REQUIRED_COLUMNS = {"Date", "Product", "Region", "Sales", "Profit"}


def load_sales_data(path=DATA_PATH):
    """Load sales data and reject incomplete or invalid records."""
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(sorted(missing))}"
        )
    if frame.empty:
        raise ValueError("Sales dataset contains no records.")

    frame = frame.copy()
    for column in ("Product", "Region"):
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Dataset contains missing {column} values.")

    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    if frame["Date"].isna().any():
        raise ValueError("Date column contains invalid or missing dates.")

    for column in ("Sales", "Profit"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any() or not np.isfinite(frame[column]).all():
            raise ValueError(f"{column} column must contain finite numeric values.")

    return frame


def summarize_sales(frame):
    """Return overall totals and sales grouped by region and product."""
    return {
        "total_sales": frame["Sales"].sum(),
        "total_profit": frame["Profit"].sum(),
        "region_sales": frame.groupby("Region")["Sales"].sum().sort_values(ascending=False),
        "product_sales": frame.groupby("Product")["Sales"].sum().sort_values(ascending=False),
    }


def main():
    df = load_sales_data()
    summary = summarize_sales(df)

    print(f"Total Sales: {summary['total_sales']:,.2f}")
    print(f"Total Profit: {summary['total_profit']:,.2f}")

    print("\\nSales by Region:")
    print(summary["region_sales"].to_string())

    print("\\nSales by Product:")
    print(summary["product_sales"].to_string())

    ax = summary["region_sales"].plot(
        kind="bar", title="Sales by Region", rot=0
    )
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
