# Walmart Store Sales Analysis

End-to-end analysis of historical weekly sales across 45 Walmart stores.

## Questions
- Which stores lead or lag in total weekly sales?
- How do sales change month to month?
- How do average and median store-week sales compare in designated holiday and non-holiday weeks?
- How are sales associated with temperature, fuel price, CPI and unemployment?

## Dataset
6,435 observations, 45 stores, February 2010 to October 2012. Fields: Store, Date, Weekly_Sales, Holiday_Flag, Temperature, Fuel_Price, CPI, Unemployment.

CSV source mirror: https://github.com/ogamircs/kaggle_walmart/blob/master/Walmart.csv. The CSV downloads to data/Walmart.csv on first run. It is not committed to this repository.

## Limits
This is weekly store-level data, not transaction or product data. It has no costs, discounts, inventory, quantity or profit fields, so this project does not calculate profit or margin. Holiday comparisons and correlations are descriptive, not causal. This is historical data, not a current Walmart report.

## Run
```bash
pip install -r requirements-dev.txt
python scripts/run_analysis.py
streamlit run app.py
pytest -q
```

The analysis writes CSV summaries, a Markdown summary and PNG charts to outputs/. The Streamlit app provides store and date filters, KPI cards, charts, tables and CSV download.
