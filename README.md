# Sales Data Analysis using Python

An end-to-end exploratory data analysis project using historical Walmart weekly store sales data. The project includes data validation, business-focused summaries, visualizations, an interactive Streamlit dashboard, automated tests, and GitHub Actions CI.

## Project overview

This project examines weekly sales across 45 stores. It answers practical questions:

- Which stores recorded the highest and lowest total weekly sales?
- How did aggregated sales vary by calendar month?
- How did average and median store-week sales differ between holiday-flagged and non-holiday weeks?
- How were weekly sales associated with temperature, fuel price, CPI, and unemployment in this dataset?

## Dataset

- Observations: 6,435 store-week records
- Stores: 45
- Period: February 2010 to October 2012
- Columns: `Store`, `Date`, `Weekly_Sales`, `Holiday_Flag`, `Temperature`, `Fuel_Price`, `CPI`, `Unemployment`

Source CSV mirror: [Walmart weekly sales dataset](https://github.com/ogamircs/kaggle_walmart/blob/master/Walmart.csv). The application downloads the CSV to `data/Walmart.csv` on first run. The dataset is not committed to this repository.

## Analysis and outputs

The analysis module validates required columns, missing and non-finite values, non-negative sales, valid holiday flags, positive store identifiers, and duplicate store-date records.

Running the analysis generates:

- `outputs/store_performance.csv`
- `outputs/monthly_sales.csv`
- `outputs/holiday_comparison.csv`
- `outputs/correlation_matrix.csv`
- `outputs/summary.md`
- `outputs/charts/top_10_stores.png`
- `outputs/charts/monthly_sales_trend.png`
- `outputs/charts/holiday_comparison.png`

The Streamlit dashboard provides store and date filters, filtered KPIs, interactive charts, a store performance table, and a filtered CSV download.

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements-dev.txt
```

## Run the project

Generate analysis tables, charts, and the Markdown summary:

```bash
python scripts/run_analysis.py
```

Launch the interactive dashboard:

```bash
streamlit run app.py
```

Run automated tests:

```bash
pytest -q
```

## Project structure

```text
.
├── .github/workflows/tests.yml
├── app.py
├── data/
├── outputs/
├── requirements.txt
├── requirements-dev.txt
├── scripts/run_analysis.py
├── src/sales_analysis.py
└── tests/test_sales_analysis.py
```

## Interpretation limits

- This is historical weekly store-level data, not a current Walmart performance report.
- The dataset does not contain product, customer, transaction, quantity, discount, inventory, cost, or profit fields. This project therefore does not calculate profit, margin, product performance, or customer behaviour.
- Holiday comparisons are descriptive. They do not establish that holidays caused sales to change.
- Correlations describe associations in this dataset. They do not establish causation.
- Monthly totals sum weekly observations by the calendar month of each observation date. They should not be interpreted as audited accounting-month revenue.

## Tools

Python, pandas, NumPy, Matplotlib, Plotly, Streamlit, pytest, and GitHub Actions.
