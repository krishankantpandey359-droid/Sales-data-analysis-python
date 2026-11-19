# Sales Data Analysis using Python

## Project overview

This project analyzes a small six-row sales dataset. It calculates total sales and profit, summarizes sales by region, product, date, and product-region combination, and creates a regional sales chart.

The dataset is intentionally small. Treat the results as a coding and analysis demonstration, not as statistically representative business performance.

## Dataset

The included `sales_data.csv` contains six records and five columns:

- `Date`
- `Product`
- `Region`
- `Sales`
- `Profit`

The script validates the required columns, non-empty product and region labels, valid dates, and finite numeric sales/profit values before analysis.

## Verified totals in the included dataset

| Metric | Value |
|---|---:|
| Records | 6 |
| Total sales | 205,000 |
| Total profit | 33,000 |

Sales by region:

| Region | Sales |
|---|---:|
| North | 85,000 |
| South | 55,000 |
| West | 45,000 |
| East | 20,000 |

Sales by product:

| Product | Sales |
|---|---:|
| Laptop | 95,000 |
| Mobile | 65,000 |
| Tablet | 45,000 |

Daily sales and the product-region cross-tabulation are also available from the analysis function. These totals describe only the six rows in the included sample.

## Project structure

```text
Sales-data-analysis-python/
├── project.py
├── sales_data.csv
├── requirements.txt
├── tests/
│   └── test_project.py
└── .github/
    └── workflows/
        └── tests.yml
```

## Setup and run

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Run the analysis:

```bash
python project.py
```

Use another CSV path:

```bash
python project.py --data path/to/your_sales.csv
```

Save the regional chart to a file:

```bash
python project.py --save-chart output/region-sales.png
```

## Run tests

```bash
pytest -q
```

The tests check dataset totals, regional and product breakdowns, daily sales, product-region totals, headless script execution, missing columns, empty files, missing labels, invalid dates, non-numeric values, infinite values, and missing files.

## Limitations and next steps

- Six records are insufficient for reliable business forecasting or general conclusions.
- The dataset has no customer, order, quantity, discount, or cost breakdown, so customer behaviour and margin drivers cannot be analyzed.
- Profit is treated as a supplied field. The project does not independently validate its accounting definition.
- Useful extensions include a larger time series, monthly trends, profit margin, product-region cross-tabulation, and data visualizations with clear units.
