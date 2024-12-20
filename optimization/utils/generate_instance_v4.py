#!/usr/bin/env python3

import json
import numpy as np
import math

base_instance_path = "./data/instances_v4/forecast_test_12_30_18_30_base.json"
output_path = "./data/instances_v4/forecast_test_12_30_18_30.json"


instance = {}
with open(base_instance_path, 'r') as file:
    instance = json.load(file)

stations = instance["stations"]
stations_cnt = len(stations)
distances = instance["distances"]
assert stations_cnt == len(distances) == len(distances[0])
print("stations_cnt:" , stations_cnt)

# id1 = 0
# id2 = np.argmax(dist_matrix[0])
# max0 = max(dist_matrix[0])
# print(id1, id2, max0)
# print(stations[id1])
# print(stations[id2])
# id1 = 0
# id2 = np.argmin(dist_matrix[0][1:]) + 1
# min0 = min(dist_matrix[0][1:])
# print(id1, id2, min0)
# print(stations[id1])
# print(stations[id2])

# TODO temporary fill in: c_reward = 1, demand = +-1
for station in stations:
    station["c_reward"] = 1
    station["s_init"] = station["id"] % 2
    station["s_goal"] = (station["id"] + 1) % 2

s_init_sum = sum([station["s_init"] for station in stations])
s_goal_sum = sum([station["s_goal"] for station in stations])
demand_sum = sum([station["s_goal"] - station["s_init"] for station in stations])
print("s_init_sum:", s_init_sum)
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
capacity = 24
for i in range(districts_cnt):
    vehicle = {
        "id": i,
        "depot_id": i, 
        "capacity": capacity
    }
    vehicles.append(vehicle)

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
