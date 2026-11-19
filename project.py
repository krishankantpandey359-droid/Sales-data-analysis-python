from pathlib import Path

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {"Date", "Product", "Region", "Sales", "Profit"}


def load_sales_data(data_path):
    """Load sales data and validate its schema and values."""
    data_path = Path(data_path)
    if not data_path.is_file():
        raise FileNotFoundError(f"Sales dataset not found: {data_path}")

    frame = pd.read_csv(data_path)
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}"
        )
    if frame.empty:
        raise ValueError("Dataset contains no sales records.")

    for column in ("Product", "Region"):
        values = frame[column].astype("string").str.strip()
        if values.isna().any() or values.eq("").any():
            raise ValueError(f"Dataset contains missing {column} values.")
        frame[column] = values

    try:
        frame["Date"] = pd.to_datetime(frame["Date"], errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Dataset contains invalid Date values.") from exc
    if frame["Date"].isna().any():
        raise ValueError("Dataset contains missing Date values.")

    for column in ("Sales", "Profit"):
        try:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Dataset contains non-numeric {column} values.") from exc

        values = frame[column].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"Dataset contains missing or non-finite {column} values.")

    return frame


def analyze_sales(frame):
    """Return headline totals and sorted sales breakdowns."""
    return {
        "total_sales": float(frame["Sales"].sum()),
        "total_profit": float(frame["Profit"].sum()),
        "profit_margin_percent": (
            float(frame["Profit"].sum() / frame["Sales"].sum() * 100)
            if frame["Sales"].sum() != 0 else None
        ),
        "region_sales": frame.groupby("Region")["Sales"].sum().sort_values(ascending=False),
        "product_sales": frame.groupby("Product")["Sales"].sum().sort_values(ascending=False),
    }


def main():
    parser = argparse.ArgumentParser(description="Explore sales by region and product.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).resolve().with_name("sales_data.csv"),
        help="Path to the sales CSV file (default: sales_data.csv beside this script).",
    )
    parser.add_argument(
        "--save-chart",
        type=Path,
        default=None,
        help="Optional path to save the regional sales chart instead of only displaying it.",
    )
    args = parser.parse_args()

    df = load_sales_data(args.data)
    results = analyze_sales(df)

    print(f"Total Sales: {results['total_sales']:,.2f}")
    print(f"Total Profit: {results['total_profit']:,.2f}")

    print("\nSales by Region:")
    print(results["region_sales"].to_string())

    print("\nSales by Product:")
    print(results["product_sales"].to_string())

    ax = results["region_sales"].plot(kind="bar", title="Sales by Region", rot=0)
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    plt.tight_layout()

    if args.save_chart:
        args.save_chart.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(args.save_chart, dpi=150, bbox_inches="tight")
        print(f"Chart saved to: {args.save_chart}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
