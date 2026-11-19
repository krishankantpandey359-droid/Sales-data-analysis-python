# Sales Data Analysis using Python

An end-to-end exploratory data analysis project using the Walmart Weekly Sales Dataset. The project includes data validation, store-level summaries, calendar-month aggregation, holiday comparisons, correlation analysis, reproducible charts, CSV exports, a Markdown report, and an interactive Streamlit dashboard.

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

Dataset source mirror: [Walmart Weekly Sales Dataset CSV](https://github.com/ogamircs/kaggle_walmart/blob/master/Walmart.csv).

The project downloads the CSV to data/walmart_weekly_sales.csv on first run. The dataset is not committed to this repository. The source is a public GitHub mirror, not a direct official Walmart endpoint.

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

## Data provenance and interpretation

- The analysis downloads a CSV from the public GitHub mirror linked above when the local file is absent.
- The linked mirror is the retrieval location used by this project. It is not represented as an official Walmart data endpoint.
- The repository does not currently establish the original publisher's licence or a canonical, immutable release identifier. Check the source terms before redistributing the dataset.
- The loader validates the complete downloaded CSV before publishing it to the data directory. It checks the required schema, dates, finite numeric values, non-negative sales, positive whole-number store IDs, binary holiday flags, and duplicate store-date keys.
- The project preserves the source field names. Temperature units, fuel-price currency, CPI base/definition, and unemployment measurement conventions are not independently documented in this repository. Treat those units and definitions as source-dependent rather than assuming them.
- Store-week sales are the observation unit. A store's total is the sum of its available weekly records, so compare totals alongside the number of reported weeks.

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
- The Walmart Weekly Sales Dataset is historical and must not be presented as a current Walmart performance report.
- Some stores may have different numbers of reported weeks. Store totals should be interpreted alongside observation counts.

## Technology stack

Python, pandas, NumPy, Matplotlib, Plotly, Streamlit, pytest, Ruff, and GitHub Actions.
