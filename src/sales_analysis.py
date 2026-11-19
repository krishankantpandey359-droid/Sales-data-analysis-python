"""Reusable data loading, validation, and analysis functions."""
from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/ogamircs/kaggle_walmart/master/Walmart.csv"
DEFAULT_DATA_PATH = Path("data/Walmart.csv")
REQUIRED_COLUMNS = ["Store", "Date", "Weekly_Sales", "Holiday_Flag", "Temperature", "Fuel_Price", "CPI", "Unemployment"]
NUMERIC_COLUMNS = ["Store", "Weekly_Sales", "Holiday_Flag", "Temperature", "Fuel_Price", "CPI", "Unemployment"]
CORRELATION_COLUMNS = ["Weekly_Sales", "Temperature", "Fuel_Price", "CPI", "Unemployment"]


def download_dataset(path: str | Path = DEFAULT_DATA_PATH) -> Path:
    """Download the public CSV mirror when the local dataset is missing."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        urlretrieve(DATA_URL, destination)
    return destination


def validate_data(data: pd.DataFrame) -> None:
    """Raise ValueError when required data-quality rules are violated."""
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Dataset is empty.")
    if data[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("Missing or invalid values found in required columns.")

    dates = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
    if dates.isna().any():
        raise ValueError("Date contains invalid values.")

    try:
        numeric = data[NUMERIC_COLUMNS].apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Numeric columns contain non-numeric values.") from exc

    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite numeric values found.")
    if (numeric["Weekly_Sales"] < 0).any():
        raise ValueError("Weekly_Sales cannot be negative.")
    if (numeric["Store"] <= 0).any():
        raise ValueError("Store identifiers must be positive.")
    if not np.equal(numeric["Store"] % 1, 0).all():
        raise ValueError("Store identifiers must be whole numbers.")
    if not numeric["Holiday_Flag"].isin([0, 1]).all():
        raise ValueError("Holiday_Flag must contain only 0 or 1.")

    keys = pd.DataFrame({"Store": numeric["Store"], "Date": dates})
    if keys.duplicated(["Store", "Date"]).any():
        raise ValueError("Duplicate Store-Date records found.")


def load_data(path: str | Path = DEFAULT_DATA_PATH, download: bool = True) -> pd.DataFrame:
    """Load, normalize, validate, and sort the weekly sales dataset."""
    source_path = Path(path)
    if not source_path.exists():
        if not download:
            raise FileNotFoundError(source_path)
        download_dataset(source_path)

    data = pd.read_csv(source_path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    data = data[REQUIRED_COLUMNS].copy()
    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    validate_data(data)

    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.to_period("M").astype(str)
    data["Holiday_Type"] = np.where(data["Holiday_Flag"].eq(1), "Holiday week", "Non-holiday week")
    return data.sort_values(["Store", "Date"]).reset_index(drop=True)


def store_performance(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize weekly sales by store and rank stores by total sales."""
    summary = (
        data.groupby("Store", as_index=False)
        .agg(
            Total_Sales=("Weekly_Sales", "sum"),
            Average_Weekly_Sales=("Weekly_Sales", "mean"),
            Median_Weekly_Sales=("Weekly_Sales", "median"),
            Sales_Std_Dev=("Weekly_Sales", "std"),
            Peak_Week_Sales=("Weekly_Sales", "max"),
            Weeks_Reported=("Weekly_Sales", "size"),
        )
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )
    summary["Sales_Rank"] = np.arange(1, len(summary) + 1)
    return summary


def monthly_sales(data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weekly observations by calendar month."""
    working = data.copy()
    if "Month" not in working.columns:
        if "Date" not in working.columns:
            raise ValueError("monthly_sales requires either a Month or Date column.")
        dates = pd.to_datetime(working["Date"], errors="coerce")
        if dates.isna().any():
            raise ValueError("Date contains invalid values; cannot derive monthly sales.")
        working["Month"] = dates.dt.to_period("M").astype(str)
    if "Weekly_Sales" not in working.columns:
        raise ValueError("monthly_sales requires a Weekly_Sales column.")
    return (
        working.groupby("Month", as_index=False)
        .agg(
            Total_Sales=("Weekly_Sales", "sum"),
            Average_Weekly_Sales=("Weekly_Sales", "mean"),
            Store_Weeks=("Weekly_Sales", "size"),
        )
        .sort_values("Month")
        .reset_index(drop=True)
    )


def holiday_comparison(data: pd.DataFrame) -> pd.DataFrame:
    """Compare store-week sales for holiday and non-holiday observations."""
    working = data.copy()
    working["Holiday_Type"] = np.where(working["Holiday_Flag"].eq(1), "Holiday week", "Non-holiday week")
    return (
        working.groupby("Holiday_Type", as_index=False)
        .agg(
            Average_Weekly_Sales=("Weekly_Sales", "mean"),
            Median_Weekly_Sales=("Weekly_Sales", "median"),
            Total_Sales=("Weekly_Sales", "sum"),
            Store_Weeks=("Weekly_Sales", "size"),
        )
    )


def correlation_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """Return Pearson correlations for sales and available numeric factors."""
    missing = sorted(set(CORRELATION_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Correlation analysis is missing columns: {missing}")
    return data[CORRELATION_COLUMNS].corr()


def headline_metrics(data: pd.DataFrame) -> dict[str, int | float | str]:
    """Calculate high-level metrics for the selected observations."""
    if data.empty:
        raise ValueError("Cannot calculate headline metrics for an empty dataset.")
    return {
        "records": int(len(data)),
        "stores": int(data["Store"].nunique()),
        "total_sales": float(data["Weekly_Sales"].sum()),
        "average_weekly_sales": float(data["Weekly_Sales"].mean()),
        "first_date": data["Date"].min().strftime("%Y-%m-%d"),
        "last_date": data["Date"].max().strftime("%Y-%m-%d"),
    }
