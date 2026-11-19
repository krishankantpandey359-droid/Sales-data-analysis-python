from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.sales_analysis import load_data,store_performance,monthly_sales,holiday_comparison,correlation_matrix,headline_metrics

def main():
    out=ROOT/"outputs"; charts=out/"charts"; charts.mkdir(parents=True,exist_ok=True)
    df=load_data(ROOT/"data"/"Walmart.csv")
    stores=store_performance(df); months=monthly_sales(df); holiday=holiday_comparison(df); corr=correlation_matrix(df); m=headline_metrics(df)
    stores.to_csv(out/"store_performance.csv",index=False); months.to_csv(out/"monthly_sales.csv",index=False); holiday.to_csv(out/"holiday_comparison.csv",index=False); corr.to_csv(out/"correlation_matrix.csv")
    fig,ax=plt.subplots(figsize=(10,5)); top=stores.head(10).sort_values("Total_Sales"); ax.barh(top.Store.astype(str),top.Total_Sales); ax.set(title="Top 10 stores by total sales",xlabel="Total weekly sales"); fig.tight_layout(); fig.savefig(charts/"top_10_stores.png",dpi=150); plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,5)); ax.plot(months.Month,months.Total_Sales,marker="o"); ax.tick_params(axis="x",rotation=60); ax.set(title="Monthly sales trend",xlabel="Month",ylabel="Total weekly sales"); fig.tight_layout(); fig.savefig(charts/"monthly_sales_trend.png",dpi=150); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,5)); ax.bar(holiday.Holiday_Type,holiday.Average_Weekly_Sales); ax.set(title="Average sales: holiday vs non-holiday",ylabel="Average store-week sales"); fig.tight_layout(); fig.savefig(charts/"holiday_comparison.png",dpi=150); plt.close(fig)
    report=f"# Analysis summary\n\n- Records: {m['records']:,}\n- Stores: {m['stores']}\n- Date range: {m['first_date']} to {m['last_date']}\n- Total sales: {m['total_sales']:,.2f}\n- Average store-week sales: {m['average_weekly_sales']:,.2f}\n\n## Top five stores\n\n{stores.head().to_string(index=False)}\n\n## Holiday comparison\n\n{holiday.to_string(index=False)}\n\n## Interpretation limits\n- Holiday comparisons and correlations are descriptive, not causal.\n- No profit, cost, inventory or product-level fields are available.\n"
    (out/"summary.md").write_text(report,encoding="utf-8")
    print(f"Completed: {m['records']} rows, {m['stores']} stores. Outputs: {out}")
if __name__=="__main__": main()
