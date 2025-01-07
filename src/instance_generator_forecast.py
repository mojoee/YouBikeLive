import sqlite3
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json
import os
import matplotlib.pyplot as plt
from utils import fetch_stations

from config import cfg

# ---------------------------------------
# Configuration
# ---------------------------------------
db_path = "./youbike_data.db"
time_of_interest_start = cfg.instance_time_start
time_of_interest_end = cfg.instance_time_end
output_dir = "./data/instances"
os.makedirs(output_dir, exist_ok=True)

default_station = {
    "sno": "unknown_sno",
    "snaen": "Unknown Station",
    "sareaen": "Unknown District",
    "latitude": 0.0,
    "longitude": 0.0,
    "capacity": 10,
    "s_init": 0,
    "s_goal": 0,
    "coords": [0.0, 0.0],
    "predicted_demand": [0] * 24  # 24 hours of zero demand
}


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def load_and_preprocess_station(station_id):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT *
    FROM youbike_status
    WHERE sno = '{station_id}'
    ORDER BY mday ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Ensure `mday` is in datetime format for resampling
    df['mday'] = pd.to_datetime(df['mday'])
    df = df.set_index('mday')

    # Drop non-numeric columns
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    df = df.drop(columns=non_numeric_cols, errors='ignore')

    # Resample and fill missing values
    df = df.resample('1h').mean().round().ffill()

    # Ensure `capacity` is present
    if 'capacity' not in df.columns:
        global df_stations
        cap = df_stations.loc[df_stations['sno'] == station_id, 'capacity']
        if len(cap) > 0:
            capacity = cap.iloc[0]
        else:
            capacity = df['available_rent_bikes'].max()  # Fallback guess
        df['capacity'] = capacity
    else:
        capacity = df['capacity'].mean()

    # Compute demand
    demands = []
    prev_bikes = None
    prev_demand = 0
    for t in df.index:
        curr_bikes = df.at[t, 'available_rent_bikes']
        if prev_bikes is None:
            demand = 0
        else:
            raw_demand = prev_bikes - curr_bikes
            if curr_bikes == 0:
                if prev_bikes > 0:
                    demand = prev_bikes
                else:
                    demand = prev_demand if prev_demand > 0 else 1
            elif curr_bikes == capacity:
                if prev_bikes < capacity:
                    demand = prev_bikes - capacity
                else:
                    demand = prev_demand if prev_demand < 0 else -1
            else:
                demand = raw_demand

        demands.append(demand)
        prev_bikes = curr_bikes
        prev_demand = demand

    df['demand'] = demands
    return df


def predict_station_demand_naive(station_id, forecast_date=None):
    df = load_and_preprocess_station(station_id)
    if df.empty:
        return [0] * 24

    if forecast_date is None:
        last_date = df.index[-1].date()
        forecast_date = (pd.to_datetime(last_date) + pd.Timedelta(days=1)).date()

    forecast_start = pd.to_datetime(forecast_date)
    forecast_end = forecast_start + pd.Timedelta(days=0, hours=23)
    hours = pd.date_range(start=forecast_start, end=forecast_end, freq='1H')

    predicted_values = []
    for hour in hours:
        prev_day = hour - pd.Timedelta(days=1)
        prev_week = hour - pd.Timedelta(days=7)
        # maybe can think about more sophisticated approach here. 

        if (prev_day in df.index) and (prev_week in df.index):
            val_prev_day = df.loc[prev_day, 'demand']
            val_prev_week = df.loc[prev_week, 'demand']
            pred = (val_prev_day + val_prev_week) / 2.0
            predicted_values.append(float(pred))
        else:
            predicted_values.append(0.0)

    return predicted_values


def find_optimal_starting_point(hourly_demands, station_capacity):
    max_demand = max(hourly_demands)
    min_demand = min(hourly_demands)
    range_demand = max_demand - min_demand
    if range_demand == 0:
        s_goal = station_capacity / 2
    else:
        s_goal = station_capacity/range_demand*max_demand
    return int(s_goal)


def get_station_capacity(df, sno, default_capacity=10):
    matching_rows = df.loc[df["sno"] == sno]
    if not matching_rows.empty:
        return int(matching_rows["capacity"].values[0])
    else:
        print(f"Warning: Station {sno} not found in df_stations. Using default capacity.")
        return default_capacity


def get_station_available_bikes_at_time(sno, time):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT *
    FROM youbike_status
    WHERE sno = '{sno}' AND mday <= '{time}'
    ORDER BY mday DESC
    LIMIT 1;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        return 0
    else:
        return int(df['available_rent_bikes'].values[0])


# Compute demands and balance s_init and s_goal
# Fetch stations data
distance_csv_path = "distance_matrix_20250106.csv"
df_distances = pd.read_csv(distance_csv_path, header=0)
# stations = df_distances.columns.tolist()
distance_matrix = df_distances.values.tolist()
df_distances.index = df_distances.columns
distance_matrix = []

for i, sno in enumerate(df_distances.columns):
    surr = []
    for j, sno_2 in enumerate(df_distances.columns):
        distance = int(df_distances[sno][sno_2])
        surr.append(distance)
    distance_matrix.append(surr)

df_stations = fetch_stations(db_path)
optimal_allocation = {}
for sno in df_distances.columns:
    hourly_demands = predict_station_demand_naive(sno)
    cap = get_station_capacity(df_stations, sno)
    s_goal = find_optimal_starting_point(hourly_demands, cap)
    # get intial
    # we need to calculate the 8 hour interval wich is best for rebalancing
    # assuming that we rebalance from 00:00 to 08:00
    s_init = get_station_available_bikes_at_time(sno, cfg.instance_start)

    optimal_allocation[sno] = (s_init, s_goal)

total_s_init = sum([optimal_allocation[sno][0] for sno in df_distances.columns])
total_s_goal = sum([optimal_allocation[sno][1] for sno in df_distances.columns])

if total_s_goal != total_s_init:
    discrepancy = total_s_init - total_s_goal
    print(f"Balancing discrepancy: {discrepancy}")
    while discrepancy != 0:
        for sno in df_distances.columns:
            if discrepancy == 0:
                break
            adjustment = np.sign(discrepancy)
            optimal_allocation[sno] = (optimal_allocation[sno][0],
                                       optimal_allocation[sno][1] + adjustment)
            discrepancy -= adjustment

# Generate instance data
stations = []
for i, sno in enumerate(df_distances.columns):
    row = df_stations[df_stations['sno'] == sno]
    station = {
        "id": i,
        "true_id": sno,
        "station_name": row['snaen'].values[0],
        "capacity": int(row['capacity'].values[0]),
        "district": row['sareaen'].values[0],
        "s_init": int(optimal_allocation[sno][0]),
        "s_goal": int(optimal_allocation[sno][1]),
        "coords": [row['latitude'].values[0], row['longitude'].values[0]],
    }
    stations.append(station)


instance = {
    "stations": stations,
    "distances": distance_matrix,
    "vehicles": {
        "count": 2,
        "capacity": 20
    }
}

name = f"instance1_{cfg.instance_start}"
output_file = f"{output_dir}/instance_forecast_{name}.json"
with open(output_file, "w") as f:
    json.dump(instance, f, cls=NumpyEncoder, indent=4)

print(f"Instance saved to {output_file}")
