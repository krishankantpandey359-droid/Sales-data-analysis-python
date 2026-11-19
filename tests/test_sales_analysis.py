import pandas as pd
import pytest
from src.sales_analysis import validate_data,store_performance,monthly_sales,holiday_comparison,correlation_matrix,load_data

@pytest.fixture
def sample():
    return pd.DataFrame({"Store":[1,1,2,2],"Date":pd.to_datetime(["2020-01-03","2020-01-10","2020-01-03","2020-01-10"]),"Weekly_Sales":[100.,200.,300.,400.],"Holiday_Flag":[0,1,0,1],"Temperature":[10.,11.,12.,13.],"Fuel_Price":[2.,2.1,2.2,2.3],"CPI":[100.,100.1,100.2,100.3],"Unemployment":[5.,5.1,5.2,5.3]})

def test_store_ranking(sample):
    r=store_performance(sample); assert r.iloc[0].Store==2 and r.iloc[0].Total_Sales==700 and r.iloc[0].Sales_Rank==1

def test_monthly_aggregation(sample):
    r=monthly_sales(sample); assert len(r)==1 and r.iloc[0].Total_Sales==1000 and r.iloc[0].Store_Weeks==4

def test_holiday_average(sample):
    r=holiday_comparison(sample).set_index("Holiday_Type"); assert r.loc["Holiday week","Average_Weekly_Sales"]==300

def test_correlation_shape(sample):
    r=correlation_matrix(sample); assert r.shape==(5,5) and r.loc["Weekly_Sales","Weekly_Sales"]==pytest.approx(1)

def test_duplicate_key_rejected(sample):
    with pytest.raises(ValueError,match="Duplicate Store-Date"): validate_data(pd.concat([sample,sample.iloc[[0]]]))

def test_negative_sales_rejected(sample):
    bad=sample.copy(); bad.loc[0,"Weekly_Sales"]=-1
    with pytest.raises(ValueError,match="negative"): validate_data(bad)

def test_bad_holiday_flag_rejected(sample):
    bad=sample.copy(); bad.loc[0,"Holiday_Flag"]=3
    with pytest.raises(ValueError,match="0 or 1"): validate_data(bad)

def test_load_parses_dates_and_month(tmp_path):
    p=tmp_path/"tiny.csv"
    pd.DataFrame({"Store":[1],"Date":["05-02-2010"],"Weekly_Sales":[123],"Holiday_Flag":[0],"Temperature":[40],"Fuel_Price":[2.5],"CPI":[200],"Unemployment":[8]}).to_csv(p,index=False)
    r=load_data(p,download=False); assert r.loc[0,"Date"]==pd.Timestamp("2010-02-05") and r.loc[0,"Month"]=="2010-02"

def test_missing_required_value_rejected(sample):
    bad = sample.copy()
    bad.loc[0, "Temperature"] = float("nan")
    with pytest.raises(ValueError, match="Missing or invalid"):
        validate_data(bad)


def test_monthly_aggregation_rejects_invalid_date():
    bad = pd.DataFrame({"Date": ["not-a-date"], "Weekly_Sales": [10]})
    with pytest.raises(ValueError, match="invalid values"):
        monthly_sales(bad)


def test_monthly_aggregation_requires_month_or_date():
    bad = pd.DataFrame({"Weekly_Sales": [10]})
    with pytest.raises(ValueError, match="Month or Date"):
        monthly_sales(bad)


def test_invalid_date_rejected_on_load(tmp_path):
    path = tmp_path / "invalid_date.csv"
    pd.DataFrame({
        "Store": [1], "Date": ["not-a-date"], "Weekly_Sales": [123],
        "Holiday_Flag": [0], "Temperature": [40], "Fuel_Price": [2.5],
        "CPI": [200], "Unemployment": [8],
    }).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Missing or invalid"):
        load_data(path, download=False)
