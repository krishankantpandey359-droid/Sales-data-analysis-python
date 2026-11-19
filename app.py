"""Interactive dashboard for the Walmart Weekly Sales Dataset."""
from pathlib import Path
from urllib.error import URLError

import pandas as pd
import plotly.express as px
import streamlit as st

from src.sales_analysis import (
    correlation_matrix,
    headline_metrics,
    holiday_comparison,
    load_data,
    monthly_sales,
    store_performance,
)

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Sales Data Analysis using Python",
    page_icon="📊",
    layout="wide",
)
st.title("Sales Data Analysis using Python")
st.caption(
    "Exploratory analysis of the Walmart Weekly Sales Dataset. "
    "Historical data only, not a current Walmart performance report."
)


@st.cache_data
def get_data():
    return load_data(ROOT / "data" / "walmart_weekly_sales.csv")


try:
    df = get_data()
except (OSError, ValueError, URLError, pd.errors.ParserError) as exc:
    st.error(f"Dataset loading failed: {exc}")
    st.info(
        "Check your internet connection or place the source CSV at "
        "data/walmart_weekly_sales.csv, then rerun the dashboard."
    )
    st.stop()

st.sidebar.header("Filters")
available_stores = sorted(df["Store"].unique().tolist())
selected_stores = st.sidebar.multiselect(
    "Stores",
    available_stores,
    default=available_stores,
)
minimum_date = df["Date"].min().date()
maximum_date = df["Date"].max().date()
selected_dates = st.sidebar.date_input(
    "Date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)

filtered = df[df["Store"].isin(selected_stores)].copy()
if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered = filtered[
            filtered["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
        ]
    elif len(selected_dates) == 1:
        filtered = filtered[
            filtered["Date"].dt.date == selected_dates[0]
        ]
else:
    filtered = filtered[
        filtered["Date"].dt.date == selected_dates
    ]

if filtered.empty:
    st.warning(
        "No records match the selected filters. Change the store or date filters."
    )
    st.stop()

metrics = headline_metrics(filtered)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Filtered records", f"{metrics['records']:,}")
kpi2.metric("Stores", metrics["stores"])
kpi3.metric("Total weekly sales", f"{metrics['total_sales']:,.2f}")
kpi4.metric(
    "Average store-week sales",
    f"{metrics['average_weekly_sales']:,.2f}",
)

store_summary = store_performance(filtered)
monthly_summary = monthly_sales(filtered)
holiday_summary = holiday_comparison(filtered)

left, right = st.columns(2)
left.plotly_chart(
    px.bar(
        store_summary.head(15).sort_values("Total_Sales"),
        x="Total_Sales",
        y="Store",
        orientation="h",
        title="Top 15 stores by total sales",
        labels={"Total_Sales": "Total weekly sales", "Store": "Store"},
    ),
    use_container_width=True,
)
right.plotly_chart(
    px.line(
        monthly_summary,
        x="Month",
        y="Total_Sales",
        markers=True,
        title="Monthly sales trend",
        labels={"Total_Sales": "Total weekly sales", "Month": "Calendar month"},
    ),
    use_container_width=True,
)

left, right = st.columns(2)
left.plotly_chart(
    px.bar(
        holiday_summary,
        x="Holiday_Type",
        y="Average_Weekly_Sales",
        title="Average sales by holiday flag",
        labels={
            "Holiday_Type": "Week type",
            "Average_Weekly_Sales": "Average store-week sales",
        },
    ),
    use_container_width=True,
)
right.plotly_chart(
    px.imshow(
        correlation_matrix(filtered),
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        title="Correlation matrix",
    ),
    use_container_width=True,
)

st.subheader("Store performance")
st.dataframe(store_summary, use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered data",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="sales_data_analysis_filtered.csv",
    mime="text/csv",
)
st.caption(
    "Holiday comparisons and correlations are descriptive, not causal. "
    "The source data has no cost or profit fields, so profit and margin are not calculated."
)
