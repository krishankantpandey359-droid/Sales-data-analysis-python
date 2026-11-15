from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "sales_data.csv"
sys.path.insert(0, str(ROOT))
from project import load_sales_data


def test_dataset_schema_and_totals():
    frame = load_sales_data(DATA)
    assert len(frame) == 6
    assert {"Date", "Product", "Region", "Sales", "Profit"}.issubset(frame.columns)
    assert frame["Sales"].sum() == 205000
    assert frame["Profit"].sum() == 33000
    assert frame.groupby("Region")["Sales"].sum().to_dict() == {
        "East": 20000, "North": 85000, "South": 55000, "West": 45000
    }


def test_analysis_script_runs_headlessly():
    result = subprocess.run(
        [sys.executable, str(ROOT / "project.py")],
        cwd=ROOT,
        env={**__import__("os").environ, "MPLBACKEND": "Agg"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Total Sales: 205,000.00" in result.stdout
    assert "Total Profit: 33,000.00" in result.stdout
    assert "Sales by Product:" in result.stdout


@pytest.mark.parametrize(
    ("column", "bad_value", "message"),
    [
        ("Sales", "not-a-number", "non-numeric Sales"),
        ("Profit", float("inf"), "non-finite Profit"),
        ("Date", "not-a-date", "invalid Date"),
        ("Region", "", "missing Region"),
    ],
)
def test_loader_rejects_invalid_values(tmp_path, column, bad_value, message):
    frame = pd.read_csv(DATA)
    frame.loc[0, column] = bad_value
    path = tmp_path / "invalid.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match=message):
        load_sales_data(path)


def test_loader_rejects_empty_dataset(tmp_path):
    frame = pd.read_csv(DATA).iloc[0:0]
    path = tmp_path / "empty.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="no sales records"):
        load_sales_data(path)
