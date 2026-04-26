import pandas as pd
import matplotlib.pyplot as plt
 
# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("weather.csv")
 
# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])
 
# Sort by Date (important for correct graph)
df = df.sort_values("Date")
 
# -------------------------
# BASIC INFO
# -------------------------
print("📊 WEATHER DATA SUMMARY")
print("-" * 30)
print("Average Temperature:", round(df["Temperature"].mean(), 2))
print("Average Humidity:", round(df["Humidity"].mean(), 2))
print("Total Rainfall:", df["Rainfall"].sum())
 
# -------------------------
# TEMPERATURE TREND
# -------------------------
plt.figure(figsize=(8,5))
 
plt.plot(
    df["Date"],
    df["Temperature"],
    marker='o',
    linewidth=2
)
 
plt.title("Temperature Trend Over Time")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
 
plt.xticks(rotation=45)
plt.grid()
 
plt.tight_layout()
 
# Save image (important for GitHub)
plt.savefig("temperature_trend.png")
 
plt.show()
 
# -------------------------
# RAINFALL ANALYSIS
# -------------------------
plt.figure(figsize=(8,5))
 
plt.bar(df["Date"], df["Rainfall"])
 
plt.title("Rainfall Analysis")
plt.xlabel("Date")
plt.ylabel("Rainfall (mm)")
 
plt.xticks(rotation=45)
plt.grid()
 
plt.tight_layout()
 
plt.savefig("rainfall_analysis.png")
 
plt.show()
 
# -------------------------
# WEATHER DISTRIBUTION (PIE)
# -------------------------
weather_counts = df["Weather"].value_counts()
 
plt.figure(figsize=(6,6))
 
weather_counts.plot(
    kind='pie',
    autopct='%1.1f%%'
)
 
plt.title("Weather Distribution")
plt.ylabel("")
 
plt.tight_layout()
 
plt.savefig("weather_distribution.png")
 
plt.show()
 
# -------------------------
# SIMPLE FORECAST
# -------------------------
forecast_temp = df["Temperature"].mean()
 
print("\n🔮 PREDICTION")
print("-" * 30)
print("Predicted Next Day Temperature:", round(forecast_temp, 2), "°C")
 
