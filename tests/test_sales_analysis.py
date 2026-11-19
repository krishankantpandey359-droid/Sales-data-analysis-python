"""Unit tests for data validation and sales-analysis functions."""
from pathlib import Path

import pandas as pd
import pytest

from src.sales_analysis import (
    correlation_matrix,
    download_dataset,
    headline_metrics,
    holiday_comparison,
    load_data,
    monthly_sales,
    store_performance,
    validate_data,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Store": [1, 1, 2, 2],
        "Date": pd.to_datetime(["2020-01-03", "2020-01-10", "2020-01-03", "2020-01-10"]),
        "Weekly_Sales": [100.0, 200.0, 300.0, 400.0],
        "Holiday_Flag": [0, 1, 0, 1],
        "Temperature": [10.0, 11.0, 12.0, 13.0],
        "Fuel_Price": [2.0, 2.1, 2.2, 2.3],
        "CPI": [100.0, 100.1, 100.2, 100.3],
        "Unemployment": [5.0, 5.1, 5.2, 5.3],
    })


def test_store_performance_ranks_and_aggregates(sample_data):
    result = store_performance(sample_data)
    assert result.iloc[0]["Store"] == 2
    assert result.iloc[0]["Total_Sales"] == 700
    assert result.iloc[0]["Sales_Rank"] == 1
    assert result.iloc[0]["Weeks_Reported"] == 2


def test_monthly_sales_aggregates_store_weeks(sample_data):
    result = monthly_sales(sample_data)
    assert len(result) == 1
    assert result.iloc[0]["Month"] == "2020-01"
    assert result.iloc[0]["Total_Sales"] == 1000
    assert result.iloc[0]["Store_Weeks"] == 4


def test_monthly_sales_rejects_invalid_date():
    invalid = pd.DataFrame({"Date": ["not-a-date"], "Weekly_Sales": [10]})
    with pytest.raises(ValueError, match="invalid values"):
        monthly_sales(invalid)


def test_monthly_sales_requires_month_or_date():
    with pytest.raises(ValueError, match="Month or Date"):
        monthly_sales(pd.DataFrame({"Weekly_Sales": [10]}))


def test_monthly_sales_requires_weekly_sales():
    with pytest.raises(ValueError, match="Weekly_Sales"):
        monthly_sales(pd.DataFrame({"Month": ["2020-01"]}))


def test_holiday_comparison_calculates_group_averages(sample_data):
    result = holiday_comparison(sample_data).set_index("Holiday_Type")
    assert result.loc["Holiday week", "Average_Weekly_Sales"] == 300
    assert result.loc["Non-holiday week", "Average_Weekly_Sales"] == 200


def test_correlation_matrix_returns_expected_shape(sample_data):
    result = correlation_matrix(sample_data)
    assert result.shape == (5, 5)
    assert result.loc["Weekly_Sales", "Weekly_Sales"] == pytest.approx(1.0)


def test_correlation_matrix_rejects_missing_column(sample_data):
    with pytest.raises(ValueError, match="missing columns"):
        correlation_matrix(sample_data.drop(columns="CPI"))


def test_headline_metrics_calculates_totals(sample_data):
    result = headline_metrics(sample_data)
    assert result["records"] == 4
    assert result["stores"] == 2
    assert result["total_sales"] == 1000
    assert result["average_weekly_sales"] == 250
    assert result["first_date"] == "2020-01-03"
    assert result["last_date"] == "2020-01-10"


def test_headline_metrics_rejects_empty_data(sample_data):
    with pytest.raises(ValueError, match="empty dataset"):
        headline_metrics(sample_data.iloc[:0])


def test_validation_rejects_duplicate_store_date(sample_data):
    duplicate = pd.concat([sample_data, sample_data.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate Store-Date"):
        validate_data(duplicate)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("Weekly_Sales", -1, "cannot be negative"),
        ("Holiday_Flag", 2, "0 or 1"),
        ("Store", 0, "must be positive"),
        ("Store", 1.5, "whole numbers"),
        ("Temperature", float("inf"), "Non-finite"),
        ("Fuel_Price", float("nan"), "Missing or invalid"),
    ],
)
def test_validation_rejects_invalid_values(sample_data, column, value, message):
    invalid = sample_data.copy()
    invalid.loc[0, column] = value
    with pytest.raises(ValueError, match=message):
        validate_data(invalid)


def test_validation_rejects_invalid_date(sample_data):
    invalid = sample_data.copy()
    invalid.loc[0, "Date"] = "not-a-date"
    with pytest.raises(ValueError, match="invalid values"):
        validate_data(invalid)


def test_validation_rejects_missing_required_column(sample_data):
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_data(sample_data.drop(columns="CPI"))


def test_validation_rejects_empty_dataset(sample_data):
    with pytest.raises(ValueError, match="empty"):
        validate_data(sample_data.iloc[:0])


def test_load_data_parses_dates_and_derives_fields(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({
        "Store": [1],
        "Date": ["05-02-2010"],
        "Weekly_Sales": [123],
        "Holiday_Flag": [0],
        "Temperature": [40],
        "Fuel_Price": [2.5],
        "CPI": [200],
        "Unemployment": [8],
    }).to_csv(csv_path, index=False)

    result = load_data(csv_path, download=False)
    assert result.loc[0, "Date"] == pd.Timestamp("2010-02-05")
    assert result.loc[0, "Month"] == "2010-02"
    assert result.loc[0, "Holiday_Type"] == "Non-holiday week"


def test_load_data_rejects_invalid_date(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    pd.DataFrame({
        "Store": [1],
        "Date": ["not-a-date"],
        "Weekly_Sales": [123],
        "Holiday_Flag": [0],
        "Temperature": [40],
        "Fuel_Price": [2.5],
        "CPI": [200],
        "Unemployment": [8],
    }).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing or invalid"):
        load_data(csv_path, download=False)


def test_load_data_raises_for_missing_file_without_download(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "missing.csv", download=False)



def test_download_dataset_rejects_invalid_csv_without_publishing(tmp_path, monkeypatch):
    destination = tmp_path / "data" / "walmart.csv"

    def fake_download(_url, output_path):
        pd.DataFrame({"unexpected": [1, 2]}).to_csv(output_path, index=False)

    monkeypatch.setattr("src.sales_analysis.urlretrieve", fake_download)

    with pytest.raises(ValueError, match="Missing required columns"):
        download_dataset(destination)

    assert not destination.exists()
    assert list(destination.parent.glob("*.download")) == []
    assert list(destination.parent.glob(".*.download")) == []


def test_download_dataset_rejects_empty_response_without_publishing(tmp_path, monkeypatch):
    destination = tmp_path / "data" / "walmart.csv"

    def fake_download(_url, output_path):
        Path(output_path).write_text("", encoding="utf-8")

    monkeypatch.setattr("src.sales_analysis.urlretrieve", fake_download)

    with pytest.raises(ValueError, match="empty file"):
        download_dataset(destination)

    assert not destination.exists()
    assert list(destination.parent.glob(".*.download")) == []



def test_download_dataset_publishes_valid_csv_atomically(tmp_path, monkeypatch):
    destination = tmp_path / "data" / "walmart.csv"
    valid = pd.DataFrame({
        "Store": [1],
        "Date": ["05-02-2010"],
        "Weekly_Sales": [123.0],
        "Holiday_Flag": [0],
        "Temperature": [40.0],
        "Fuel_Price": [2.5],
        "CPI": [200.0],
        "Unemployment": [8.0],
    })

    def fake_download(_url, output_path):
        valid.to_csv(output_path, index=False)

    monkeypatch.setattr("src.sales_analysis.urlretrieve", fake_download)

    result = download_dataset(destination)

    assert result == destination
    assert destination.is_file()
    assert pd.read_csv(destination).shape == (1, 8)
    assert list(destination.parent.glob(".*.download")) == []


def test_download_dataset_keeps_existing_file_without_network_call(tmp_path, monkeypatch):
    destination = tmp_path / "data" / "existing.csv"
    destination.parent.mkdir(parents=True)
    destination.write_text("existing data", encoding="utf-8")

    def unexpected_download(*_args):
        raise AssertionError("Existing dataset should not be downloaded again.")

    monkeypatch.setattr("src.sales_analysis.urlretrieve", unexpected_download)

    assert download_dataset(destination) == destination
    assert destination.read_text(encoding="utf-8") == "existing data"
