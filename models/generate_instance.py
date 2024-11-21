#!/usr/bin/env python3

import numpy as np
import random
import json
import sys

STATIONS_CNT = int(sys.argv[1])
CAPACITIES = [10, 15, 20, 25, 30]
ST_MAX_CAPACITY = np.max(CAPACITIES)

VEHICLES_CNT = 5
VEHICLES_CAPACITY = 20

MAX_COORD = 1000

s_init_sum = 0
s_goal_sum = 0

random.seed(0)


# Generate stations
stations = []
for id in range(STATIONS_CNT):
    cap_id = random.randint(0, len(CAPACITIES) - 1)
    capacity = CAPACITIES[cap_id]

    s_init = random.randint(0, capacity)
    s_goal = random.randint(0, capacity)
    s_init_sum += s_init
    s_goal_sum += s_goal
    
    x = random.randint(0, MAX_COORD)
    y = random.randint(0, MAX_COORD)

    station = {"id": id, "capacity": capacity, "s_init": s_init, "s_goal": s_goal, "coords": [x, y]}
    stations.append(station)

# Fix initial and goal states sum
while s_init_sum < s_goal_sum:
    id = random.randint(0, STATIONS_CNT - 1)
    if stations[id]["s_init"] < stations[id]["capacity"]:
        stations[id]["s_init"] += 1
        s_init_sum += 1

while s_init_sum > s_goal_sum:
    id = random.randint(0, STATIONS_CNT - 1)
    if stations[id]["s_init"] > 0:
        stations[id]["s_init"] -= 1
        s_init_sum -= 1


# distance matrix 
distances = []
for s1 in stations:
    row = []
    for s2 in stations:
        dist = np.linalg.norm(np.array(s1["coords"]) - np.array(s2["coords"]))
        row.append(dist)
    distances.append(row)


# depot
depot = {
    "capacity": 0,
    "s_init": 0,
    "s_goal": 0,
    "coords": [random.randint(0, MAX_COORD), random.randint(0, MAX_COORD)]
}
dtd = []
depot_coords = np.array(depot["coords"])
for station in stations:
    station_coords = np.array(station["coords"])
    dist = np.linalg.norm(depot_coords - station_coords)
    dtd.append(dist)
depot["dists_from_depot"] = dtd
depot["dists_to_depot"] = dtd

# vehicles
vehicles = {
    "count": VEHICLES_CNT,
    "capacity": VEHICLES_CAPACITY
    }

# final dict

data = {
    "depot": depot,
    "stations": stations, 
    "distances": distances, 
    "vehicles": vehicles
}

data_string = json.dumps(data, indent=4)

output_path = "./data/n" + str(STATIONS_CNT) + "-" + str(ST_MAX_CAPACITY) + "_v" + str(VEHICLES_CNT) + "-" + str(VEHICLES_CAPACITY) + ".json"

with open(output_path, "w") as outfile:
    outfile.write(data_string)
    print("Exported instance", output_path)