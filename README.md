# Sales Data Analysis using Python

This repository contains two clearly separated exercises: the original six-row sales-summary exercise and an extended analysis of the UCI Online Retail transaction dataset.

## Track 1: Original six-row exercise

The root-level `sales_data.csv` remains the small teaching example used by `project.py`. It contains six records and five fields: Date, Product, Region, Sales and Profit.

Verified sample totals: Sales 205,000 and Profit 33,000. These are totals for the six included rows only. The sample has no external dataset provenance and is not statistically representative.

Run it with:

```bash
python project.py
pytest -q
```

## Track 2: UCI Online Retail, 541,909 source records

The extended workflow downloads the original UCI Online Retail workbook at runtime. The source describes transactions from a UK-based non-store retailer between 1 December 2010 and 9 December 2011.

- Dataset page: https://archive.ics.uci.edu/dataset/352/online+retail
- Download archive: https://archive.ics.uci.edu/static/public/352/online+retail.zip
- DOI: https://doi.org/10.24432/C5BW33
- Creator: Daqing Chen
- Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Original source size: 541,909 invoice-line records

The script derives line sales as `Quantity * UnitPrice`. UnitPrice is recorded in pounds sterling (GBP). It excludes cancellation invoices (InvoiceNo starting with C), non-positive quantities, non-positive unit prices, invalid dates and blank invoice numbers. Missing CustomerID records remain in overall sales totals but are not counted as identified customers.

The source does not provide product cost. This track does not calculate profit or profit margin. Do not confuse derived sales revenue with profit.

The successful automated run on 20 November 2026 produced the following result from the downloaded source archive (SHA-256 is recorded in the artifact's `summary.json`):

| Measure | Verified result |
|---|---:|
| Source invoice-line rows | 541,909 |
| Included completed sales lines | 530,104 |
| Excluded rows | 11,805 |
| Invoices | 19,960 |
| Identified customers | 4,338 |
| Product codes | 3,922 |
| Countries | 38 |
| Derived sales | GBP 10,666,684.54 |
| Included date range | 1 December 2010–9 December 2011 |
| Included rows missing CustomerID | 132,220 |

The exclusion counters in `summary.json` are diagnostic counts by condition and overlap; do not add them to calculate the total excluded rows. The report records the exact UTC retrieval time and archive hash for this run.

### Run the extended analysis

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the downloader, cleaning and analysis:

```bash
python scripts/run_online_retail_analysis.py
```

The archive is cached under `data/raw/`. Reports are written to `outputs/online_retail/`:

- `summary.json`: source, retrieval time, archive SHA-256, data-quality audit and headline measures.
- `monthly_sales.csv`: monthly sales, invoices, lines and identified customers.
- `country_sales.csv`: sales and invoice count by country.
- `top_20_products.csv`: highest-revenue stock-code and product-description combinations.

The original workbook is downloaded at runtime and is not committed to this repository. GitHub Actions performs the same download and uploads the generated reports as the `uci-online-retail-analysis` artifact.

### Reproduce locally

```bash
pytest -q
python scripts/run_online_retail_analysis.py
```

## Project limitations

- The six-row file is retained only as a small coding example.
- The UCI source is historical and represents one retailer, not the entire market.
- Cancellations and negative or zero quantity/price lines are excluded from the completed-sales analysis.
- Some invoice lines do not have CustomerID. They are retained for overall sales but excluded from the identified-customer count.
- No cost field is supplied, so profit and margin are not available.
- Sales are calculated in the dataset's GBP price units. No inflation adjustment or currency conversion is performed.

## Technologies

Python, Pandas, NumPy, Matplotlib, openpyxl, pytest and GitHub Actions.

## Attribution

Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. Licensed under CC BY 4.0.


## Latest GitHub Actions validation

Latest successful main-branch workflow run verified on 26 November 2026: [GitHub Actions run #45800495879](https://github.com/krishankantpandey359-droid/Sales-data-analysis-python/actions/runs/45800495879). This confirms the configured automated checks, not every manual or deployment feature.
