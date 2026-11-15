from pathlib import Path
import os
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_dataset_schema_and_summary_totals():
    data = pd.read_csv(ROOT / "sales_data.csv")
    assert len(data) == 6
    assert {"Date", "Product", "Region", "Sales", "Profit"} <= set(data.columns)
    assert data["Sales"].sum() == 205000
    assert data["Profit"].sum() == 33000
    assert data.groupby("Region")["Sales"].sum().to_dict() == {
        "East": 20000,
        "North": 85000,
        "South": 55000,
        "West": 45000,
    }


def test_analysis_script_runs_headlessly():
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    result = subprocess.run(
        [sys.executable, str(ROOT / "project.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Total Sales: 205,000.00" in result.stdout
    assert "Total Profit: 33,000.00" in result.stdout
