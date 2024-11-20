#!/usr/bin/env python3

import numpy as np
import random


STATIONS_CNT = 10
CAPACITIES = [10, 15, 20, 25, 30]

VEHICLES_CNT = 5
VEHICLES_CAPACITY = 20

MAX_COORD = 1000

s_init_sum = 0
s_goal_sum = 0

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

