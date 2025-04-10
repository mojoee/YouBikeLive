import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import RandomForestRegressor

# Load dataset
data_file = "./data/prediction/processed_data_all_stations_weather_500101002.csv"  # Updated data directory
df = pd.read_csv(data_file)

# Convert timestamp to datetime and sort
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.sort_values("timestamp", inplace=True)

# Define feature sets
bike_features = ["available_rent_bikes", "available_return_bikes", "capacity"]
weather_features = ["temperature", "wind_speed", "humidity", "pressure", "rainfall"]
all_features = bike_features + weather_features

# Perform correlation analysis (excluding station_id)
correlation = df.drop(columns=["youbike_station_id"]).corr()["demand"].sort_values(ascending=False)
print("Feature Correlation with Demand:\n", correlation)

# Plot correlation heatmap (excluding station_id)
plt.figure(figsize=(8, 6))
sns.heatmap(df.drop(columns=["youbike_station_id"]).corr(), annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
plt.title("Feature Correlation Heatmap")
plt.savefig("./results/correlation_heatmap.png", dpi=300, bbox_inches="tight")
print("Correlation heatmap saved as 'correlation_heatmap.png'")

# Normalize data
scaler = MinMaxScaler()
df[bike_features + ["demand"]] = scaler.fit_transform(df[bike_features + ["demand"]])
df[weather_features] = scaler.fit_transform(df[weather_features])

# Train-test split
train_size = int(len(df) * 0.8)
df_train, df_test = df[:train_size], df[train_size:]

# Train models with and without weather features
def train_model(X_train, y_train, X_test, model_type):
    if model_type == "ARIMA":
        model = ARIMA(y_train, order=(5,1,0)).fit()
        return model.forecast(steps=len(X_test))
    elif model_type == "SARIMA":
        model = SARIMAX(y_train, order=(1,1,1), seasonal_order=(1,1,1,24)).fit()
        return model.forecast(steps=len(X_test))
    elif model_type == "XGBoost":
        model = XGBRegressor(n_estimators=100, learning_rate=0.1)
        model.fit(X_train, y_train)
        return model.predict(X_test)
    elif model_type == "RandomForest":
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        return model.predict(X_test)

# Prepare datasets
X_train_bike, X_test_bike = df_train[bike_features], df_test[bike_features]
X_train_all, X_test_all = df_train[all_features], df_test[all_features]
y_train, y_test = df_train["demand"], df_test["demand"]

# Train models
models = ["ARIMA", "SARIMA", "XGBoost", "RandomForest"]
results = []

for model in models:
    pred_bike = train_model(X_train_bike, y_train, X_test_bike, model)
    pred_all = train_model(X_train_all, y_train, X_test_all, model)
    
    results.append({
        "Model": model,
        "MAE (No Weather)": mean_absolute_error(y_test, pred_bike),
        "MSE (No Weather)": mean_squared_error(y_test, pred_bike),
        "MAPE (No Weather)": np.mean(np.abs((y_test - pred_bike) / y_test)) * 100,
        "MAE (With Weather)": mean_absolute_error(y_test, pred_all),
        "MSE (With Weather)": mean_squared_error(y_test, pred_all),
        "MAPE (With Weather)": np.mean(np.abs((y_test - pred_all) / y_test)) * 100
    })

# Convert to DataFrame
results_df = pd.DataFrame(results)
results_df.to_csv("./results/weather_impact_comparison.csv", index=False)

# Plot Comparison
fig, axes = plt.subplots(3, 1, figsize=(10, 15))
metrics = ["MAE", "MSE", "MAPE"]
colors = ["Oranges", "Purples", "Reds"]

def plot_metric(ax, metric, color):
    melted_df = results_df.melt(id_vars=["Model"], value_vars=[f"{metric} (No Weather)", f"{metric} (With Weather)"], var_name="Condition", value_name=metric)
    sns.barplot(x="Model", y=metric, hue="Condition", data=melted_df, palette=color, ax=ax)
    ax.set_title(f"{metric} Comparison: No Weather vs. With Weather")
    ax.set_xticklabels(results_df["Model"], rotation=45)
    ax.set_ylabel(metric)

for i, (metric, color) in enumerate(zip(metrics, colors)):
    plot_metric(axes[i], metric, color)

plt.tight_layout()
plt.savefig("./results/weather_impact_comparison.png", dpi=300, bbox_inches="tight")
print("Weather impact comparison plot saved as 'weather_impact_comparison.png'")