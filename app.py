from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT))
import plotly.express as px
import streamlit as st
from src.sales_analysis import load_data,store_performance,monthly_sales,holiday_comparison,correlation_matrix,headline_metrics

st.set_page_config(page_title="Walmart Store Sales Analysis",page_icon="📊",layout="wide")
st.title("Walmart Store Sales Analysis")
st.caption("Historical weekly store sales. Descriptive analysis, not a current company report.")
@st.cache_data
def get_data(): return load_data(ROOT/"data"/"Walmart.csv")
try: df=get_data()
except Exception as e: st.error(f"Dataset loading failed: {e}"); st.stop()
m=headline_metrics(df); a,b,c,d=st.columns(4)
a.metric("Records",f"{m['records']:,}"); b.metric("Stores",m["stores"]); c.metric("Total sales",f"{m['total_sales']:,.0f}"); d.metric("Avg store-week",f"{m['average_weekly_sales']:,.0f}")
st.sidebar.header("Filters")
available=sorted(df.Store.unique().tolist()); selected=st.sidebar.multiselect("Stores",available,default=available)
lo,hi=df.Date.min().date(),df.Date.max().date(); dates=st.sidebar.date_input("Date range",(lo,hi),min_value=lo,max_value=hi)
f=df[df.Store.isin(selected)].copy()
if isinstance(dates,tuple) and len(dates)==2: f=f[f.Date.between(dates[0],dates[1])]
if f.empty: st.warning("No rows match these filters."); st.stop()
s=store_performance(f); mo=monthly_sales(f); h=holiday_comparison(f)
x,y=st.columns(2)
x.plotly_chart(px.bar(s.tail(15).sort_values("Total_Sales"),x="Total_Sales",y="Store",orientation="h",title="Top stores"),use_container_width=True)
y.plotly_chart(px.line(mo,x="Month",y="Total_Sales",markers=True,title="Monthly sales trend"),use_container_width=True)
x,y=st.columns(2)
x.plotly_chart(px.bar(h,x="Holiday_Type",y="Average_Weekly_Sales",title="Average sales by holiday flag"),use_container_width=True)
y.plotly_chart(px.imshow(correlation_matrix(f),text_auto=".2f",zmin=-1,zmax=1,color_continuous_scale="RdBu_r",title="Correlation matrix"),use_container_width=True)
st.subheader("Store KPI table"); st.dataframe(s,use_container_width=True,hide_index=True)
st.download_button("Download filtered CSV",f.to_csv(index=False).encode(),file_name="filtered_walmart_sales.csv",mime="text/csv")
st.caption("Holiday differences and correlations are descriptive, not causal. No profit metric is calculated because cost/profit fields are absent.")
