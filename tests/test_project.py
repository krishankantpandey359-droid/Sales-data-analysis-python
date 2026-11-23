from pathlib import Path
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "sales_data.csv"
sys.path.insert(0, str(ROOT))

from project import analyze_sales, load_sales_data


def test_dataset_schema_and_totals():
    frame = load_sales_data(DATA)
    assert len(frame) == 6
    assert {"Date", "Product", "Region", "Sales", "Profit"}.issubset(frame.columns)
    assert frame["Sales"].sum() == 205000
    assert frame["Profit"].sum() == 33000
    assert frame.groupby("Region")["Sales"].sum().to_dict() == {
        "East": 20000, "North": 85000, "South": 55000, "West": 45000
    }


def test_analysis_returns_business_metrics_and_ranked_breakdowns():
    result = analyze_sales(load_sales_data(DATA))
    assert result["record_count"] == 6
    assert result["total_sales"] == 205000
    assert result["total_profit"] == 33000
    assert result["profit_margin_pct"] == pytest.approx(33000 / 205000 * 100)
    assert result["region_sales"].index.tolist() == ["North", "South", "West", "East"]
    assert result["product_sales"].to_dict() == {
        "Laptop": 95000, "Mobile": 65000, "Tablet": 45000
    }
    assert result["region_profit"].to_dict() == {
        "North": 14000, "West": 7000, "South": 9000, "East": 3000
    }
    assert result["product_profit"].to_dict() == {
        "Laptop": 15000, "Mobile": 11000, "Tablet": 7000
    }
    assert result["monthly_sales"].to_dict() == {"2024-01": 205000}
    assert result["daily_sales"].sum() == 205000
    assert len(result["daily_sales"]) == 6
    assert result["product_region_sales"].to_numpy().sum() == 205000
    assert result["product_region_sales"].loc["Laptop", "North"] == 50000


def test_zero_sales_has_undefined_margin():
    frame = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01"]),
        "Product": ["A"], "Region": ["North"], "Sales": [0], "Profit": [0]
    })
    assert analyze_sales(frame)["profit_margin_pct"] is None


def test_analysis_script_runs_headlessly_and_prints_metrics():
    result = subprocess.run(
        [sys.executable, str(ROOT / "project.py")],
        cwd=ROOT,
        env={**os.environ, "MPLBACKEND": "Agg"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Records Analyzed: 6" in result.stdout
    assert "Total Sales: 205,000.00" in result.stdout
    assert "Total Profit: 33,000.00" in result.stdout
    assert "Overall Profit Margin: 16.10%" in result.stdout
    assert "Sales by Region:" in result.stdout
    assert "Profit by Region:" in result.stdout
    assert "Sales by Product:" in result.stdout
    assert "Profit by Product:" in result.stdout
    assert "Sales by Month:" in result.stdout


@pytest.mark.parametrize(
    ("column", "bad_value", "message"),
    [
        ("Sales", "not-a-number", "non-numeric Sales"),
        ("Profit", np.inf, "non-finite Profit"),
        ("Sales", -np.inf, "non-finite Sales"),
        ("Date", "not-a-date", "invalid Date"),
        ("Date", np.nan, "missing Date"),
        ("Region", "", "missing Region"),
        ("Product", "   ", "missing Product"),
        ("Sales", np.nan, "non-finite Sales"),
    ],
)
def test_loader_rejects_invalid_values(tmp_path, column, bad_value, message):
    frame = pd.read_csv(DATA)
    frame[column] = frame[column].astype(object)
    frame.loc[0, column] = bad_value
    path = tmp_path / "invalid.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match=message):
        load_sales_data(path)


def test_loader_rejects_missing_required_column(tmp_path):
    frame = pd.read_csv(DATA).drop(columns=["Profit"])
    path = tmp_path / "missing-column.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="Profit"):
        load_sales_data(path)


def test_loader_rejects_empty_dataset(tmp_path):
    frame = pd.read_csv(DATA).iloc[0:0]
    path = tmp_path / "empty.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="no sales records"):
        load_sales_data(path)


def test_loader_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_sales_data(tmp_path / "does-not-exist.csv")
