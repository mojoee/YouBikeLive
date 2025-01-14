#!/usr/bin/env python3

import json
import numpy as np
import math

base_instance_path = "./data/instances_v4/instance_forecast_test_2024-12-28 00_00_01.json"
output_path = "./data/instances_v4/24-12-28.json"


instance = {}
with open(base_instance_path, 'r') as file:
    instance = json.load(file)

stations = instance["stations"]
stations_cnt = len(stations)
distances = instance["distances"]
assert stations_cnt == len(distances) == len(distances[0])
print("stations_cnt:" , stations_cnt)


# temporary fill in: c_reward = 1, demand = +-1
total_capacity = sum([station["capacity"] for station in stations])
s_init_sum = sum([station["s_init"] for station in stations])
rel_occupancy = s_init_sum / total_capacity

print("total_capacity:", total_capacity)
print("s_init_sum:", s_init_sum)
print("rel_occupancy:", rel_occupancy)

for station in stations:
    station["c_reward"] = 1
    station["s_goal"] = int(rel_occupancy * station["capacity"])
s_goal_sum = sum([station["s_goal"] for station in stations])

while s_goal_sum < s_init_sum:
    station = np.random.choice(stations)
    if station["s_goal"] < station["capacity"]:
        station["s_goal"] += 1
        s_goal_sum += 1

demand_sum = sum([station["s_goal"] - station["s_init"] for station in stations])
print("s_goal_sum:", s_goal_sum)
print("demand_sum:", demand_sum)
print()
# assert s_init_sum == s_goal_sum

# ADD DEPOTS
# one central depot per district
depots = []
districts = []
d_stations_cnts = []
for station in stations:
    district = station["district"]
    if district not in districts:
        districts.append(district)
districts_cnt = len(districts)

print("districts_cnt:", districts_cnt)
for i in range(districts_cnt):
    district = districts[i]
    d_stations = [st for st in stations if st["district"] == district]
    d_stations_cnts.append(len(d_stations))
    cand_best = {}
    dist_sum_best = math.inf
    for cand in d_stations:
        dist_sum = 0
        for d_station in d_stations:
            dist_sum += distances[cand["id"]][d_station["id"]]
        if dist_sum < dist_sum_best:
            dist_sum_best = dist_sum
            cand_best = cand

    print(i, district, d_stations_cnts[i])
    depot = {"id": i,
             "true_id": cand_best["true_id"],
             "district": cand_best["district"],
             "coords": cand_best["coords"], 
             "dists_from_depot": distances[cand_best["id"]], 
             "dists_to_depot": distances[:][cand_best["id"]]
             }
    depots.append(depot)

# ADD VEHICLES
vehicles = []
capacities = [12, 24, 24] # per district
vehicle_id = 0
for district_id in range(districts_cnt):
    for capacity in capacities:
        vehicle = {
            "id": vehicle_id,
            "depot_id": district_id, 
            "capacity": capacity
        }
        vehicles.append(vehicle)
        vehicle_id += 1

# CONSTANTS
constants = { # in seconds
    "parking_time": 180,
    "loading_time":60, 
    "max_trip_duration": 8 * 60 * 60
}

# EXPORT
data = {
    "depots": depots,
    "stations": stations, 
    "distances": distances, 
    "vehicles": vehicles,
    "constants": constants
}

data_string = json.dumps(data, indent=4)
# print(data_string)

with open(output_path, "w") as outfile:
    outfile.write(data_string)
    print("Exported instance", output_path)
