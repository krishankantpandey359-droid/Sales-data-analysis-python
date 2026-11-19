"""Generate reproducible CSV, chart, and Markdown analysis outputs."""
from pathlib import Path

import matplotlib.pyplot as plt

from src.sales_analysis import (
    correlation_matrix,
    headline_metrics,
    holiday_comparison,
    load_data,
    monthly_sales,
    store_performance,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"


def save_store_chart(summary):
    top = summary.head(10).sort_values("Total_Sales")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top["Store"].astype(str), top["Total_Sales"])
    ax.set(
        title="Top 10 stores by total sales",
        xlabel="Total weekly sales",
        ylabel="Store",
    )
    fig.tight_layout()
    fig.savefig(CHART_DIR / "top_10_stores.png", dpi=160)
    plt.close(fig)


def save_monthly_chart(summary):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(summary["Month"], summary["Total_Sales"], marker="o")
    ax.tick_params(axis="x", rotation=60)
    ax.set(
        title="Monthly sales trend",
        xlabel="Calendar month",
        ylabel="Total weekly sales",
    )
    fig.tight_layout()
    fig.savefig(CHART_DIR / "monthly_sales_trend.png", dpi=160)
    plt.close(fig)


def save_holiday_chart(summary):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(summary["Holiday_Type"], summary["Average_Weekly_Sales"])
    ax.set(
        title="Average sales: holiday vs non-holiday",
        xlabel="Week type",
        ylabel="Average store-week sales",
    )
    fig.tight_layout()
    fig.savefig(CHART_DIR / "holiday_comparison.png", dpi=160)
    plt.close(fig)


def write_summary(metrics, stores, holiday):
    report = f"""# Sales Data Analysis using Python

## Walmart Weekly Sales Dataset

- Records: {metrics["records"]:,}
- Stores: {metrics["stores"]}
- Date range: {metrics["first_date"]} to {metrics["last_date"]}
- Sum of store-week sales: {metrics["total_sales"]:,.2f}
- Average store-week sales: {metrics["average_weekly_sales"]:,.2f}

## Top five stores by total sales

{stores.head(5).to_string(index=False)}

## Holiday comparison

{holiday.to_string(index=False)}

## Interpretation limits

- Weekly observations are grouped by calendar month for the monthly summary.
- Holiday comparisons and correlations are descriptive, not causal.
- The dataset has no cost or profit fields, so profit and margin are not calculated.
"""
    (OUTPUT_DIR / "summary.md").write_text(report, encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data(ROOT / "data" / "walmart_weekly_sales.csv")
    stores = store_performance(data)
    months = monthly_sales(data)
    holiday = holiday_comparison(data)
    correlations = correlation_matrix(data)
    metrics = headline_metrics(data)

    stores.to_csv(OUTPUT_DIR / "store_performance.csv", index=False)
    months.to_csv(OUTPUT_DIR / "monthly_sales.csv", index=False)
    holiday.to_csv(OUTPUT_DIR / "holiday_comparison.csv", index=False)
    correlations.to_csv(OUTPUT_DIR / "correlation_matrix.csv")
    save_store_chart(stores)
    save_monthly_chart(months)
    save_holiday_chart(holiday)
    write_summary(metrics, stores, holiday)
    print(
        f"Analysis completed: {metrics['records']:,} records "
        f"across {metrics['stores']} stores."
    )


if __name__ == "__main__":
    main()
