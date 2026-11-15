from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Load the dataset from the same directory as this script.
data_path = Path(__file__).resolve().with_name("sales_data.csv")
df = pd.read_csv(data_path)

required_columns = {"Product", "Region", "Sales", "Profit"}
missing_columns = required_columns.difference(df.columns)
if missing_columns:
    raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}")

# Overall performance
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
print(f"Total Sales: {total_sales:,.2f}")
print(f"Total Profit: {total_profit:,.2f}")

# Sales breakdowns
region_sales = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
product_sales = df.groupby("Product")["Sales"].sum().sort_values(ascending=False)

print("\nSales by Region:")
print(region_sales.to_string())

print("\nSales by Product:")
print(product_sales.to_string())

# Visualize sales by region
ax = region_sales.plot(kind="bar", title="Sales by Region", rot=0)
ax.set_xlabel("Region")
ax.set_ylabel("Sales")
plt.tight_layout()
plt.show()
