import time
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from xgboost import XGBRegressor
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Load dataset
data_file = "processed_data_all_stations_weather_500101003"
df = pd.read_csv(f"./data/prediction/{data_file}.csv")

# Convert timestamp to datetime and sort
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.sort_values("timestamp", inplace=True)

# Feature selection
features = ["available_rent_bikes", "available_return_bikes", "capacity",
            "temperature", "wind_speed", "humidity", "pressure", "rainfall"]

# Normalize data
scaler = MinMaxScaler()
df[features + ["demand"]] = scaler.fit_transform(df[features + ["demand"]])

# Prepare time series dataset
def create_time_series(data, n_past=24, n_future=24):
    X, y = [], []
    for i in range(len(data) - n_past - n_future):
        X.append(data[i:i+n_past])  
        y.append(data[i+n_past:i+n_past+n_future, -1])  
    return np.array(X), np.array(y)

# Convert dataframe to numpy array
data_array = df[features + ["demand"]].values
X, y = create_time_series(data_array)

# Train-test split (80% train, 20% test)
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

timings = {}

### LSTM Model ###
start_time = time.time()
model = Sequential([
    LSTM(50, activation='relu', return_sequences=True, input_shape=(24, X.shape[2])),
    LSTM(50, activation='relu'),
    Dense(24)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_test, y_test), verbose=1)
timings["LSTM Training Time (s)"] = time.time() - start_time

# Predict with LSTM
start_time = time.time()
latest_input = X_test[-1].reshape(1, 24, X.shape[2])
lstm_pred = model.predict(latest_input)[0]
lstm_pred = scaler.inverse_transform(np.c_[np.zeros((24, len(features))), lstm_pred])[:, -1]
timings["LSTM Inference Time (s)"] = time.time() - start_time

### ARIMA Model ###
def train_arima(train_data, future_steps=24):
    model = ARIMA(train_data, order=(5,1,0))
    arima_model = model.fit()
    return arima_model.forecast(steps=future_steps)

start_time = time.time()
arima_train = df["demand"][:split]
arima_pred = train_arima(arima_train, future_steps=24)
timings["ARIMA Training & Inference Time (s)"] = time.time() - start_time

### SARIMA Model (Seasonal ARIMA) ###
start_time = time.time()
sarima_model = SARIMAX(arima_train, order=(1,1,1), seasonal_order=(1,1,1,24))
sarima_fit = sarima_model.fit()
sarima_pred = sarima_fit.forecast(steps=24)
timings["SARIMA Training & Inference Time (s)"] = time.time() - start_time

### Random Forest Model ###
start_time = time.time()
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
X_rf_train = X_train.reshape(X_train.shape[0], -1)
X_rf_test = X_test.reshape(X_test.shape[0], -1)
rf_model.fit(X_rf_train, y_train.reshape(y_train.shape[0], -1))
timings["Random Forest Training Time (s)"] = time.time() - start_time

start_time = time.time()
rf_pred = rf_model.predict(X_rf_test[-1].reshape(1, -1))[0]
rf_pred = scaler.inverse_transform(np.c_[np.zeros((24, len(features))), rf_pred])[:, -1]
timings["Random Forest Inference Time (s)"] = time.time() - start_time

### XGBoost Model ###
start_time = time.time()
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1)
xgb_model.fit(X_rf_train, y_train.reshape(y_train.shape[0], -1))
timings["XGBoost Training Time (s)"] = time.time() - start_time

start_time = time.time()
xgb_pred = xgb_model.predict(X_rf_test[-1].reshape(1, -1))[0]
xgb_pred = scaler.inverse_transform(np.c_[np.zeros((24, len(features))), xgb_pred])[:, -1]
timings["XGBoost Inference Time (s)"] = time.time() - start_time

### Prophet Model ###
start_time = time.time()
prophet_df = df[["timestamp", "demand"]].rename(columns={"timestamp": "ds", "demand": "y"})
prophet_model = Prophet()
prophet_model.fit(prophet_df.iloc[:split])  
timings["Prophet Training Time (s)"] = time.time() - start_time

start_time = time.time()
future = prophet_model.make_future_dataframe(periods=24, freq="H")
prophet_pred = prophet_model.predict(future)["yhat"].iloc[-24:].values
timings["Prophet Inference Time (s)"] = time.time() - start_time

# Compute Metrics
def compute_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    return mae, mse, mape

# Select last 24 actual values for evaluation
actual_values = df["demand"].iloc[-24:].values

# Calculate metrics for all models
lstm_metrics = compute_metrics(actual_values, lstm_pred)
arima_metrics = compute_metrics(actual_values, arima_pred)
sarima_metrics = compute_metrics(actual_values, sarima_pred)
rf_metrics = compute_metrics(actual_values, rf_pred)
xgb_metrics = compute_metrics(actual_values, xgb_pred)
prophet_metrics = compute_metrics(actual_values, prophet_pred)

# Create results DataFrame
results = pd.DataFrame({
    "Model": ["LSTM", "ARIMA", "SARIMA", "Random Forest", "XGBoost", "Prophet"],
    "MAE": [lstm_metrics[0], arima_metrics[0], sarima_metrics[0], rf_metrics[0], xgb_metrics[0], prophet_metrics[0]],
    "MSE": [lstm_metrics[1], arima_metrics[1], sarima_metrics[1], rf_metrics[1], xgb_metrics[1], prophet_metrics[1]],
    "MAPE (%)": [lstm_metrics[2], arima_metrics[2], sarima_metrics[2], rf_metrics[2], xgb_metrics[2], prophet_metrics[2]]
})

# Save results
results.to_csv(f"./results/model_comparison_{data_file}.csv", index=False)
timings_df = pd.DataFrame(list(timings.items()), columns=["Model", "Time (s)"])
timings_df.to_csv(f"./results/training_times_{data_file}.csv", index=False)

print("Results saved. Training and inference times:")
print(timings_df)
