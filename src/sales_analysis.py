from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/ogamircs/kaggle_walmart/master/Walmart.csv"
DEFAULT_DATA_PATH = Path("data/Walmart.csv")
REQUIRED_COLUMNS = ["Store","Date","Weekly_Sales","Holiday_Flag","Temperature","Fuel_Price","CPI","Unemployment"]
NUMERIC_COLUMNS = ["Store","Weekly_Sales","Holiday_Flag","Temperature","Fuel_Price","CPI","Unemployment"]

def download_dataset(path=DEFAULT_DATA_PATH):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists(): urlretrieve(DATA_URL,path)
    return path

def validate_data(df):
    missing=sorted(set(REQUIRED_COLUMNS)-set(df.columns))
    if missing: raise ValueError(f"Missing required columns: {missing}")
    if df.empty: raise ValueError("Dataset is empty.")
    if df[REQUIRED_COLUMNS].isna().any().any(): raise ValueError("Missing or invalid values found.")
    if not np.isfinite(df[NUMERIC_COLUMNS].to_numpy(dtype=float)).all(): raise ValueError("Non-finite numeric values found.")
    if (df.Weekly_Sales<0).any(): raise ValueError("Weekly_Sales cannot be negative.")
    if (df.Store<=0).any(): raise ValueError("Store identifiers must be positive.")
    if not df.Holiday_Flag.isin([0,1]).all(): raise ValueError("Holiday_Flag must contain only 0 or 1.")
    if df.duplicated(["Store","Date"]).any(): raise ValueError("Duplicate Store-Date records found.")

def load_data(path=DEFAULT_DATA_PATH,download=True):
    path=Path(path)
    if not path.exists():
        if not download: raise FileNotFoundError(path)
        download_dataset(path)
    df=pd.read_csv(path)
    missing=sorted(set(REQUIRED_COLUMNS)-set(df.columns))
    if missing: raise ValueError(f"Dataset is missing required columns: {missing}")
    df=df[REQUIRED_COLUMNS].copy()
    df["Date"]=pd.to_datetime(df.Date,dayfirst=True,errors="coerce")
    for c in NUMERIC_COLUMNS: df[c]=pd.to_numeric(df[c],errors="coerce")
    validate_data(df)
    df["Year"]=df.Date.dt.year
    df["Month"]=df.Date.dt.to_period("M").astype(str)
    df["Holiday_Type"]=np.where(df.Holiday_Flag.eq(1),"Holiday week","Non-holiday week")
    return df.sort_values(["Store","Date"]).reset_index(drop=True)

def store_performance(df):
    out=df.groupby("Store",as_index=False).agg(Total_Sales=("Weekly_Sales","sum"),Average_Weekly_Sales=("Weekly_Sales","mean"),Median_Weekly_Sales=("Weekly_Sales","median"),Sales_Std_Dev=("Weekly_Sales","std"),Peak_Week_Sales=("Weekly_Sales","max"),Weeks_Reported=("Weekly_Sales","size"))
    out=out.sort_values("Total_Sales",ascending=False).reset_index(drop=True); out["Sales_Rank"]=np.arange(1,len(out)+1)
    return out

def monthly_sales(df):
    return df.groupby("Month",as_index=False).agg(Total_Sales=("Weekly_Sales","sum"),Average_Weekly_Sales=("Weekly_Sales","mean"),Store_Weeks=("Weekly_Sales","size")).sort_values("Month").reset_index(drop=True)

def holiday_comparison(df):
    d=df.assign(Holiday_Type=np.where(df.Holiday_Flag.eq(1),"Holiday week","Non-holiday week"))
    return d.groupby("Holiday_Type",as_index=False).agg(Average_Weekly_Sales=("Weekly_Sales","mean"),Median_Weekly_Sales=("Weekly_Sales","median"),Store_Weeks=("Weekly_Sales","size"))

def correlation_matrix(df):
    cols=["Weekly_Sales","Temperature","Fuel_Price","CPI","Unemployment"]
    return df[cols].corr(numeric_only=True)

def headline_metrics(df):
    return {"records":int(len(df)),"stores":int(df.Store.nunique()),"total_sales":float(df.Weekly_Sales.sum()),"average_weekly_sales":float(df.Weekly_Sales.mean()),"first_date":df.Date.min().strftime("%Y-%m-%d"),"last_date":df.Date.max().strftime("%Y-%m-%d")}
