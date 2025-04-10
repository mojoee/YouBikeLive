import pandas as pd
import numpy as np
import json
import os
import sys
from DBIO import YouBikeDataManager
from config import cfg
from demand_prediction import DemandPredictionContext, \
                              NaiveDemandPredictionStrategy, \
                              ProphetDemandPredictionStrategy, \
                              WeeklyAverageDemandPredictionStrategy, \
                              GroundTruthDemandPredictionStrategy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimization.utils.inventory_policies import min_P_max_policy, min_Q_total_policy

# ---------------------------------------
# Configuration
# ---------------------------------------
db_path = "./youbike_data.db"
data_manager = YouBikeDataManager(db_path)
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

if cfg.prediction_strategy == "prophet":
    context = DemandPredictionContext(ProphetDemandPredictionStrategy(data_manager))
elif cfg.prediction_strategy == "naive":
    context = DemandPredictionContext(NaiveDemandPredictionStrategy(data_manager))
elif cfg.prediction_strategy == "weekly":
    context = DemandPredictionContext(WeeklyAverageDemandPredictionStrategy(data_manager))
else:
    raise ValueError(f"Invalid prediction strategy: {cfg.prediction_strategy}")

# Create a separate context for ground truth data
ground_truth_context = DemandPredictionContext(GroundTruthDemandPredictionStrategy(data_manager))

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def simulate_inventory(hourly_demands, station_capacity, starting_inventory):
    overflow_count = 0
    shortage_count = 0
    inventory = starting_inventory

    for demand in hourly_demands:
        # Update inventory
        inventory = max(0, min(station_capacity, inventory - demand))

        # Check overflow and shortage
        if inventory == station_capacity:
            overflow_count += 1
        elif inventory == 0:
            shortage_count += 1

    return overflow_count, shortage_count


def get_station_capacity(df, sno, default_capacity=10):
    matching_rows = df.loc[df["sno"] == sno]
    if not matching_rows.empty:
        return int(matching_rows["capacity"].values[0])
    else:
        print(f"Warning: Station {sno} not found in df_stations. Using default capacity.")
        return default_capacity


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

df_stations = data_manager.fetch_stations()
optimal_allocation = {}
total_bikes = sum([data_manager.get_station_available_bikes_at_time(sno, cfg.instance_start) for sno in df_distances.columns])
total_capacity = sum([get_station_capacity(df_stations, sno) for sno in df_distances.columns])
for sno in df_distances.columns:
    hourly_demands = context.predict_demand(station_id=sno, forecast_date=cfg.instance_start)
    real_demands = ground_truth_context.predict_demand(station_id=sno, forecast_date=cfg.instance_start)
    cap = get_station_capacity(df_stations, sno)
    s_init = data_manager.get_station_available_bikes_at_time(sno, cfg.instance_start)
    if cfg.inventory_strategy == "min_peak":
        s_goal = min_P_max_policy(hourly_demands, cap)
        s_goal_real = min_P_max_policy(real_demands, cap)
    elif cfg.inventory_strategy == "nochange":
        s_goal = s_init
        s_goal_real = s_init
    elif cfg.inventory_strategy == "proportional":
        s_goal = int((cap / total_capacity) * total_bikes)
        s_goal_real = s_goal
    elif cfg.inventory_strategy == "min_total":
        s_goal = min_Q_total_policy(hourly_demands, cap)
        s_goal_real = min_Q_total_policy(real_demands, cap)
    else:
        print(f"Invalid inventory strategy: {cfg.inventory_strategy}")
    # get intial
    # we need to calculate the 8 hour interval wich is best for rebalancing
    # assuming that we rebalance from 00:00 to 08:00

    optimal_allocation[sno] = (s_init, s_goal, s_goal_real)

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
                                       optimal_allocation[sno][1] + adjustment,
                                       optimal_allocation[sno][2])
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
        "real_s_goal": int(optimal_allocation[sno][2]),
        "demand": context.predict_demand(station_id=sno, forecast_date=cfg.instance_start),
        "real_demand": ground_truth_context.predict_demand(station_id=sno, forecast_date=cfg.instance_start),
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

name = f"instance_{cfg.prediction_strategy}_{cfg.instance_start}_{cfg.inventory_strategy}"
output_file = f"{output_dir}/instance_forecast_{name}.json"
with open(output_file, "w") as f:
    json.dump(instance, f, cls=NumpyEncoder, indent=4)

print(f"Instance saved to {output_file}")
