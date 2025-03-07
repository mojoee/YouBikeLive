#!/usr/bin/env python3

import numpy as np
import random
import json
import sys


CNTS = [2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
CAPACITIES = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100]
PARKING_TIME = 120
LOADING_TIME = 60
MAX_TRIP_TIME = 60 * 60 * 8
MAX_COORD = 1000

for STATIONS_CNT in CNTS:
    DEPOTS_CNT = STATIONS_CNT // 100
    VEHICLES_CNT = 4 * DEPOTS_CNT

    # Fill VEHICLES_CAPACITY alternately with 12 and 24
    VEHICLES_CAPACITY = [12 if i % 2 == 0 else 24 for i in range(VEHICLES_CNT)]

    # Fill VEHICLES_DEPOTS with numbers from 0 to DEPOTS_CNT, each appearing four times
    VEHICLES_DEPOTS = [i for i in range(DEPOTS_CNT) for _ in range(4)]

    s_init_sum = 0
    s_goal_sum = 0

    random.seed(0)

    # STATIONS
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

        station = {"id": id, "capacity": capacity, "s_init": s_init, "s_goal": s_goal, "coords": [x, y], "c_reward": 1}
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


    # DISTANCE MATRIX
    distances = []
    for s1 in stations:
        row = []
        for s2 in stations:
            dist = int(np.linalg.norm(np.array(s1["coords"]) - np.array(s2["coords"])))
            row.append(dist)
        distances.append(row)


    # DEPOTS
    depots = []

    for i in range(DEPOTS_CNT):
        depot = {
            "id": i,
            "capacity": 0,
            "s_init": 0,
            "s_goal": 0,
            "coords": [random.randint(0, MAX_COORD), random.randint(0, MAX_COORD)]
        }
        dtd = []
        depot_coords = np.array(depot["coords"])
        for station in stations:
            station_coords = np.array(station["coords"])
            dist = int(np.linalg.norm(depot_coords - station_coords))
            dtd.append(dist)
        depot["dists_from_depot"] = dtd
        depot["dists_to_depot"] = dtd
        depots.append(depot)


    # VEHICLES
    vehicles = []
    for i in range(VEHICLES_CNT):
        vehicle = {
            "id": i,
            "depot_id": VEHICLES_DEPOTS[i],
            "capacity": VEHICLES_CAPACITY[i]
            }
        vehicles.append(vehicle)

    # CONSTANTS
    constants = {
        "parking_time": PARKING_TIME,
        "loading_time": LOADING_TIME,
        "max_trip_time": MAX_TRIP_TIME
    }


    # final dict
    data = {
        "depots": depots,
        "stations": stations, 
        "distances": distances, 
        "vehicles": vehicles,
        "constants": constants
    }


    data_string = json.dumps(data, indent=None)
    # print(data_string)

    output_path = "./data/instances_v4/rnd_large/" + str(STATIONS_CNT) + "_v" + str(VEHICLES_CNT) + "_d" + str(DEPOTS_CNT) + ".json"

    with open(output_path, "w") as outfile:
        outfile.write(data_string)
        print("Exported instance", output_path)
