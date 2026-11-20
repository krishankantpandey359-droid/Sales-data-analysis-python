from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from online_retail import clean_online_retail, summarize_online_retail


        "InvoiceNo": ["10001", "10001", "C10002", "10003", "10004"],
        "StockCode": ["A", "B", "C", "D", "E"],
        "Description": ["Widget", "Cable", "Cancelled", "Return", "Free item"],
        "Quantity": [2, 1, 1, -1, 3],
        "InvoiceDate": ["01/12/2010 08:30", "01/12/2010 08:31",
                        "01/12/2010 09:00", "02/12/2010 10:00", "03/12/2010 11:00"],
        "UnitPrice": [10.0, 5.0, 10.0, 5.0, 0.0],
        "CustomerID": [12345, None, 12345, 99999, 99999],
        "Country": ["United Kingdom", "United Kingdom", "United Kingdom",
                    "France", "France"],
    })


def test_cleaning_excludes_cancellations_and_non_positive_lines():
    clean, audit = clean_online_retail(sample_data())
    assert len(clean) == 2
    assert clean["Sales"].sum() == 25.0
    assert audit["source_rows"] == 5
    assert audit["included_sales_lines"] == 2
    assert audit["cancellation_rows"] == 1
    assert audit["non_positive_quantity_rows"] == 1
    assert audit["non_positive_unit_price_rows"] == 1
    assert audit["rows_missing_customer_id_retained"] == 1


def test_summary_keeps_unknown_customer_sales_in_revenue():
    clean, _ = clean_online_retail(sample_data())
    summary, tables = summarize_online_retail(clean)
    assert summary["total_sales_gbp"] == 25.0
    assert summary["customer_count_non_missing"] == 1
    assert summary["invoice_count"] == 1
    assert summary["currency"] == "GBP (pounds sterling)"
    assert "Profit" not in clean.columns
    assert tables["monthly_sales.csv"]["Sales"].sum() == 25.0
    assert tables["country_sales.csv"]["Country"].tolist() == ["United Kingdom"]


def test_cleaner_rejects_missing_schema():
    with pytest.raises(ValueError, match="missing columns"):
        clean_online_retail(pd.DataFrame({"InvoiceNo": ["1"]}))
