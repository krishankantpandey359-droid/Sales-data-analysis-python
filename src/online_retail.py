"""Analysis helpers for the UCI Online Retail transaction dataset.

UCI Online Retail is licensed CC BY 4.0. Revenue is derived as Quantity *
UnitPrice in GBP. The source does not contain product cost, so this module
intentionally does not calculate profit or margin.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd

UCI_DATASET_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
UCI_DATASET_PAGE = "https://archive.ics.uci.edu/dataset/352/online+retail"
UCI_DOI = "https://doi.org/10.24432/C5BW33"
REQUIRED_COLUMNS = {
    "InvoiceNo", "StockCode", "Description", "Quantity",
    "InvoiceDate", "UnitPrice", "CustomerID", "Country",
}


def download_dataset(cache_dir: Path, refresh: bool = False) -> tuple[Path, str]:
    """Download the official UCI ZIP if it is not already cached."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive_path = cache_dir / "uci-online-retail.zip"
    if refresh or not archive_path.is_file():
        request = urllib.request.Request(
            UCI_DATASET_URL,
            headers={"User-Agent": "SalesDataAnalysisPortfolio/1.0"},
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read()
        if not payload:
            raise ValueError("UCI returned an empty Online Retail archive.")
        archive_path.write_bytes(payload)

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    return archive_path, digest


def read_source_archive(archive_path: Path) -> pd.DataFrame:
    """Read the original workbook directly from the UCI ZIP archive."""
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise FileNotFoundError(f"UCI archive not found: {archive_path}")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            candidates = [
                name for name in archive.namelist()
                if Path(name).name.lower() == "online retail.xlsx"
            ]
            if not candidates:
                raise ValueError("UCI ZIP does not contain Online Retail.xlsx.")
            workbook = archive.read(candidates[0])
    except zipfile.BadZipFile as exc:
        raise ValueError("Downloaded UCI file is not a valid ZIP archive.") from exc
    return pd.read_excel(BytesIO(workbook), engine="openpyxl")


def clean_online_retail(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Keep completed, positive-value invoice lines and preserve missing IDs."""
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"UCI Online Retail data is missing columns: {sorted(missing)}")
    if raw.empty:
        raise ValueError("UCI Online Retail dataset contains no records.")

    frame = raw.copy(deep=True)
    frame["InvoiceNo"] = frame["InvoiceNo"].astype("string").str.strip()
    frame["StockCode"] = frame["StockCode"].astype("string").str.strip()
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame["UnitPrice"] = pd.to_numeric(frame["UnitPrice"], errors="coerce")
    frame["InvoiceDate"] = pd.to_datetime(
        frame["InvoiceDate"], errors="coerce", dayfirst=True
    )

    invoice_valid = frame["InvoiceNo"].notna() & frame["InvoiceNo"].ne("")
    cancellation = frame["InvoiceNo"].str.upper().str.startswith("C", na=False)
    positive_quantity = np.isfinite(frame["Quantity"]) & (frame["Quantity"] > 0)
    positive_price = np.isfinite(frame["UnitPrice"]) & (frame["UnitPrice"] > 0)
    valid_date = frame["InvoiceDate"].notna()
    keep = invoice_valid & ~cancellation & positive_quantity & positive_price & valid_date

    cleaned = frame.loc[keep].copy()
    cleaned["Sales"] = cleaned["Quantity"] * cleaned["UnitPrice"]
    cleaned["Description"] = (
        cleaned["Description"].fillna("Unknown description").astype(str).str.strip()
    )
    cleaned["Country"] = cleaned["Country"].fillna("Unknown country").astype(str).str.strip()
    cleaned["Month"] = cleaned["InvoiceDate"].dt.to_period("M").astype(str)

    if cleaned.empty:
        raise ValueError("No valid completed sales lines remained after validation.")
    sales = cleaned["Sales"].to_numpy(dtype=float)
    if not np.isfinite(sales).all():
        raise ValueError("Derived sales contain missing or non-finite values.")

    audit = {
        "source_rows": int(len(frame)),
        "included_sales_lines": int(len(cleaned)),
        "excluded_rows": int(len(frame) - len(cleaned)),
        "cancellation_rows": int(cancellation.sum()),
        "non_positive_quantity_rows": int((~positive_quantity).sum()),
        "non_positive_unit_price_rows": int((~positive_price).sum()),
        "invalid_date_rows": int((~valid_date).sum()),
        "rows_missing_customer_id_retained": int(cleaned["CustomerID"].isna().sum()),
        "currency": "GBP (pounds sterling)",
        "date_start": cleaned["InvoiceDate"].min().date().isoformat(),
        "date_end": cleaned["InvoiceDate"].max().date().isoformat(),
    }
    return cleaned, audit


def summarize_online_retail(cleaned: pd.DataFrame) -> tuple[dict, dict[str, pd.DataFrame]]:
    """Create reproducible monthly, country and product sales summaries."""
    monthly = (
        cleaned.groupby("Month", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            InvoiceCount=("InvoiceNo", "nunique"),
            LineCount=("InvoiceNo", "size"),
            CustomerCount=("CustomerID", "nunique"),
        )
        .sort_values("Month")
    )
    country = (
        cleaned.groupby("Country", as_index=False)
        .agg(Sales=("Sales", "sum"), InvoiceCount=("InvoiceNo", "nunique"))
        .sort_values("Sales", ascending=False)
    )
    products = (
        cleaned.groupby(["StockCode", "Description"], as_index=False)
        .agg(Sales=("Sales", "sum"), Quantity=("Quantity", "sum"),
             InvoiceCount=("InvoiceNo", "nunique"))
        .sort_values("Sales", ascending=False)
        .head(20)
    )
    summary = {
        "dataset": "UCI Online Retail",
        "source_url": UCI_DATASET_PAGE,
        "doi": UCI_DOI,
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "source_description": (
            "Transactions from a UK-based non-store online retailer. "
            "Derived sales include positive-quantity, positive-unit-price invoice lines "
            "and exclude cancellation invoices."
        ),
        "included_sales_lines": int(len(cleaned)),
        "invoice_count": int(cleaned["InvoiceNo"].nunique()),
        "customer_count_non_missing": int(cleaned["CustomerID"].nunique()),
        "product_code_count": int(cleaned["StockCode"].nunique()),
        "country_count": int(cleaned["Country"].nunique()),
        "total_sales_gbp": round(float(cleaned["Sales"].sum()), 2),
        "date_start": cleaned["InvoiceDate"].min().date().isoformat(),
        "date_end": cleaned["InvoiceDate"].max().date().isoformat(),
        "note": (
            "The source does not provide product cost. Profit and profit margin "
            "are not calculated. Missing CustomerID rows remain in overall sales "
            "totals but are not counted as identified customers."
        ),
    }
    return summary, {
        "monthly_sales.csv": monthly,
        "country_sales.csv": country,
        "top_20_products.csv": products,
    }


def run_analysis(archive_path: Path, output_dir: Path, archive_sha256: str) -> dict:
    """Run the analysis and persist CSV and JSON evidence."""
    raw = read_source_archive(archive_path)
    cleaned, audit = clean_online_retail(raw)
    summary, tables = summarize_online_retail(cleaned)
    report = {
        **summary,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "archive_sha256": archive_sha256,
        "data_quality_audit": audit,
        "method": {
            "sales_formula": "Quantity * UnitPrice",
            "date_interpretation": "day-first parsing of source InvoiceDate",
            "filters": [
                "exclude invoices whose InvoiceNo begins with C",
                "exclude Quantity <= 0 or non-numeric quantities",
                "exclude UnitPrice <= 0 or non-numeric unit prices",
                "exclude missing or invalid InvoiceDate and blank InvoiceNo",
            ],
        },
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, table in tables.items():
        table.to_csv(output_dir / filename, index=False)
    (output_dir / "summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report
