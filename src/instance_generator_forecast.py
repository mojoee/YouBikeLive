import sqlite3
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json
import os
import matplotlib.pyplot as plt

from config import cfg

# ---------------------------------------
# Configuration
# ---------------------------------------
db_path = "./youbike_data.db"
time_of_interest = cfg.instance_time
output_dir = "./data/instances"
os.makedirs(output_dir, exist_ok=True)

def fetch_stations(time_of_interest):
    conn = sqlite3.connect(db_path)
    query = f"""
    WITH RankedStations AS (
        SELECT 
            sno, 
            snaen, 
            latitude, 
            longitude, 
            total AS capacity, 
            available_rent_bikes AS s_init, 
            mday,
            ROW_NUMBER() OVER (PARTITION BY sno ORDER BY mday ASC) AS rank
        FROM youbike_data
        WHERE strftime('%H:%M', mday) >= '{time_of_interest}'
    )
    SELECT 
        sno, 
        snaen, 
        latitude, 
        longitude, 
        capacity, 
        s_init, 
        mday
    FROM RankedStations
    WHERE rank = 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df_stations = fetch_stations(time_of_interest)

# Compute s_goal as before
total_bikes = df_stations['s_init'].sum()
total_capacity = df_stations['capacity'].sum()
proportions = (df_stations['capacity'] / total_capacity) * total_bikes
df_stations['s_goal_int'] = proportions.astype(int)
df_stations['fraction'] = proportions - df_stations['s_goal_int']
remaining_bikes = total_bikes - df_stations['s_goal_int'].sum()
df_stations = df_stations.sort_values(by='fraction', ascending=False)
df_stations.iloc[:remaining_bikes, df_stations.columns.get_loc('s_goal_int')] += 1
df_stations['s_goal'] = df_stations['s_goal_int']
df_stations = df_stations.drop(columns=['s_goal_int', 'fraction'])
df_stations.reset_index(drop=True, inplace=True)


def load_and_preprocess_station(station_id):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT *
    FROM youbike_data
    WHERE sno = '{station_id}'
    ORDER BY mday ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['srcUpdateTime'] = pd.to_datetime(df['srcUpdateTime'])
    df = df.sort_values('srcUpdateTime').set_index('srcUpdateTime')
    df = df.dropna(subset=['available_rent_bikes'])

    # Drop non-numeric columns if they still exist after previous steps
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    df = df.drop(columns=non_numeric_cols, errors='ignore')

    # Now select numeric columns only for the resample and mean operation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df = df[numeric_cols].resample('1h').mean().ffill()
    # Compute demand:
    # Normally: demand(t) = available_bikes(t-1) - available_bikes(t)
    # But we adjust if station is empty or full.
    if 'capacity' not in df.columns:
        # If capacity isn't present in the data, we need it.
        # Ideally, capacity is known from df_stations. Let's just merge it.
        # We'll assume we can load capacity from df_stations.
        # If multiple stations share the same ID, we need a lookup.
        # For simplicity, just fetch from df_stations once.
        global df_stations
        cap = df_stations.loc[df_stations['sno'] == station_id, 'capacity']
        if len(cap) > 0:
            capacity = cap.iloc[0]
        else:
            capacity = df['available_rent_bikes'].max()  # fallback guess
        df['capacity'] = capacity
    else:
        capacity = df['capacity'].mean()  # assuming stable capacity

    # We'll compute demand hour by hour
    demands = []
    prev_bikes = None
    prev_demand = 0  # Store previous hour's demand to handle consecutive empties/full stations
    for t in df.index:
        curr_bikes = df.at[t, 'available_rent_bikes']
        if prev_bikes is None:
            # First hour no demand calculation possible
            demand = 0
        else:
            raw_demand = prev_bikes - curr_bikes
            # Check station status
            if curr_bikes == 0:
                # Station empty. If we see a drop from prev_bikes to 0, set demand = prev_bikes
                # If it stays empty (prev_bikes=0 too), assume same as previous hour's demand to indicate unserved demand
                if prev_bikes > 0:
                    demand = prev_bikes
                else:
                    # consecutive empty hours, assume same unserved demand as previous hour
                    demand = prev_demand if prev_demand > 0 else 1  # at least 1 bike demanded
            elif curr_bikes == capacity:
                # Station full. If we see an increase to full, negative demand = returns.
                # If previously less, demand = prev_bikes - capacity (typically negative).
                # If consecutive full, assume same negative demand pattern continues.
                if prev_bikes < capacity:
                    demand = prev_bikes - capacity
                else:
                    # consecutive full hours, assume same negative demand as previous hour
                    demand = prev_demand if prev_demand < 0 else -1
            else:
                # Normal case: just use raw_demand
                demand = raw_demand

        demands.append(demand)
        prev_bikes = curr_bikes
        prev_demand = demand

    df['demand'] = demands
    return df


def predict_station_demand_naive(station_id, forecast_date=None):
    df = load_and_preprocess_station(station_id)
    if df.empty:
        return [0]*24

    if forecast_date is None:
        last_date = df.index[-1].date()
        forecast_date = (pd.to_datetime(last_date) + pd.Timedelta(days=1)).date()

    # demand(t) = (demand(t-1day) + demand(t-1week))/2
    forecast_start = pd.to_datetime(forecast_date)
    forecast_end = forecast_start + pd.Timedelta(hours=23)
    hours = pd.date_range(start=forecast_start, end=forecast_end, freq='1H')

    predicted_values = []
    for hour in hours:
        prev_day = hour - pd.Timedelta(days=1)
        prev_week = hour - pd.Timedelta(days=7)

        if (prev_day in df.index) and (prev_week in df.index):
            val_prev_day = df.loc[prev_day, 'demand']
            val_prev_week = df.loc[prev_week, 'demand']
            pred = (val_prev_day + val_prev_week) / 2.0
            predicted_values.append(float(pred))
        else:
            predicted_values.append(0.0)

    return predicted_values


predicted_demands = {}
for sno in df_stations['sno'].unique():
    hourly_demands = predict_station_demand_naive(sno)
    predicted_demands[sno] = hourly_demands

depot = {
    "capacity": 0,
    "s_init": 0,
    "s_goal": 0,
    "coords": [25.02000, 121.53300]
}

station_coords = df_stations[['latitude', 'longitude']].values
depot_coords = np.array(depot['coords'])
dists_from_depot = [geodesic(depot_coords, station).meters for station in station_coords]
dists_to_depot = dists_from_depot[:]

num_stations = len(station_coords)
distances = np.zeros((num_stations, num_stations))
for i in range(num_stations):
    for j in range(num_stations):
        distances[i][j] = geodesic(station_coords[i], station_coords[j]).meters

stations = []
for idx, row in df_stations.iterrows():
    sno = row['sno']
    station = {
        "id": idx,
        "true_id": sno,
        "station name": row['snaen'],
        "capacity": row['capacity'],
        "district": row['sareaen'],
        "s_init": row['s_init'],
        "s_goal": row['s_goal'],
        "coords": [row['latitude'], row['longitude']],
        "predicted_demand": predicted_demands[sno]
    }
    stations.append(station)

instance = {
    "depot": {
        "capacity": depot['capacity'],
        "s_init": depot['s_init'],
        "s_goal": depot['s_goal'],
        "coords": depot['coords'],
        "dists_from_depot": dists_from_depot,
        "dists_to_depot": dists_to_depot
    },
    "stations": stations,
    "distances": distances.tolist(),
    "vehicles": {
        "count": 2,
        "capacity": 20
    }
}

name = f"test_{time_of_interest}"
output_file = f"{output_dir}/instance_forecast_{name}.json"
with open(output_file, "w") as f:
    json.dump(instance, f, indent=4)

print(f"Instance saved to {output_file}")
