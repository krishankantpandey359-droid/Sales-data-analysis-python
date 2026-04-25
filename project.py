import pandas as pd
import matplotlib.pyplot as plt
 
# Load data
df = pd.read_csv("sales_data.csv")
 
# Total Sales
total_sales = df["Sales"].sum()
print("Total Sales:", total_sales)
 
# Sales by Region
region_sales = df.groupby("Region")["Sales"].sum()
print("\nSales by Region:")
print(region_sales)
 
# Plot graph
region_sales.plot(kind='bar')
 
plt.title("Sales by Region")
plt.xlabel("Region")
plt.ylabel("Sales")
 
plt.show()
plt.show
 
