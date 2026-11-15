from pathlib import Path
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "sales_data.csv"


def test_dataset_schema_and_totals():
    frame = pd.read_csv(DATA)
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
