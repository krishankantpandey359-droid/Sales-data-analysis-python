# Sales Data Analysis using Python

An end-to-end exploratory data analysis project using historical Walmart weekly store sales data. The project includes data validation, store-level summaries, calendar-month aggregation, holiday comparisons, correlation analysis, reproducible charts, CSV exports, a Markdown report, and an interactive Streamlit dashboard.

## Business questions

- Which stores recorded the highest total weekly sales?
- How did store-week sales aggregate across calendar months?
- How did sales differ between holiday-flagged and non-holiday observations?
- How were weekly sales associated with temperature, fuel price, CPI, and unemployment?

## Dataset

| Attribute | Description |
|---|---|
| Observations | 6,435 store-week records |
| Stores | 45 |
| Period | February 2010 to October 2012 |
| Measure | Weekly_Sales |
| Other fields | Store, Date, Holiday_Flag, Temperature, Fuel_Price, CPI, Unemployment |

Dataset source mirror: [Walmart weekly sales CSV](https://github.com/ogamircs/kaggle_walmart/blob/master/Walmart.csv).

The project downloads the CSV to data/Walmart.csv on first run. The dataset is not committed to this repository. The source is a public GitHub mirror, not a direct official Walmart endpoint.

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

## Features

- Validates required columns, missing values, dates, numeric values, finite values, non-negative sales, positive whole-number store IDs, holiday flags, and duplicate store-date records.
- Calculates store totals, average and median weekly sales, standard deviation, peak week sales, observation counts, and rank.
- Aggregates weekly observations by calendar month.
- Compares holiday and non-holiday store-week observations.
- Calculates Pearson correlations for weekly sales and available numeric factors.
- Exports analysis tables, charts, and a Markdown summary.
- Provides a Streamlit dashboard with store/date filters, KPIs, interactive charts, a data table, and CSV download.
- Runs automated tests and code-quality checks through GitHub Actions.

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
pip install -r requirements-dev.txt
```

## Run

Generate analysis outputs:

```bash
python scripts/run_analysis.py
```

Launch the dashboard:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest -q
```

Run lint checks:

```bash
ruff check src scripts app.py tests
```

## Generated outputs

- outputs/store_performance.csv
- outputs/monthly_sales.csv
- outputs/holiday_comparison.csv
- outputs/correlation_matrix.csv
- outputs/summary.md
- outputs/charts/top_10_stores.png
- outputs/charts/monthly_sales_trend.png
- outputs/charts/holiday_comparison.png

## Methodology and limitations

- Each row represents one store's weekly sales observation.
- Monthly totals sum weekly observations by the calendar month of each observation date. They are not audited accounting-month revenue.
- Holiday comparisons are descriptive. They do not prove that holidays caused sales to change.
- Correlation measures association, not causation.
- The dataset has no product, customer, transaction, quantity, discount, inventory, cost, or profit fields. This project does not calculate profit, margin, product performance, or customer behaviour.
- The data is historical and must not be presented as a current Walmart performance report.
- Some stores may have different numbers of reported weeks. Store totals should be interpreted alongside observation counts.

## Technology stack

Python, pandas, NumPy, Matplotlib, Plotly, Streamlit, pytest, Ruff, and GitHub Actions.
