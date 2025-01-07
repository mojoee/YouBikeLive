#!/usr/bin/env python3

import json
import os

master_instance = "data/instances_v4/v12-24-24_b8h_d12.json"


# 1) GENERATE DISTRICT-WISE SUBPROBLEMS
data = {}
with open(master_instance, 'r') as file:
    data = json.load(file)

# Extract districts
districts = []
for station in data["stations"]:
    dd = [station["district"], station["district"].split(' ')[0]] # full name, short name
    if dd not in districts:
        districts.append(dd)

# Subdirectory for subproblems
instance_subdir = master_instance.replace(".json", "/")
os.makedirs(instance_subdir, exist_ok=True)

# for dd in [districts[-1]]:
for dd in districts:
    sub_instance = instance_subdir + dd[1] + ".json"
    # Extract stations
    sub_stations = [st for st in data["stations"] if st["district"] == dd[0]]
    stations_cnt = len(sub_stations)
    print(dd[1])
    print("stations_cnt:", stations_cnt)

    # Extract distance matrix
    distances = data["distances"]
    sub_distances = [[0] * stations_cnt for _ in range(stations_cnt)]
    for i in range(stations_cnt):
        for j in range(stations_cnt):
            id1 = sub_stations[i]["id"]
            id2 = sub_stations[j]["id"]
            sub_distances[i][j] = distances[id1][id2]
            sub_distances[j][i] = distances[id2][id1]

    # Extract depot
    sub_depots = [dp for dp in data["depots"] if dp["district"] == dd[0]]
    for sub_depot in sub_depots:
        sub_dfd = []
        sub_dtd = []
        for st in sub_stations:
            id = st["id"]
            sub_dfd.append(sub_depot["dists_from_depot"][id])
            sub_dtd.append(sub_depot["dists_to_depot"][id])
        sub_depot["dists_from_depot"] = sub_dfd
        sub_depot["dists_to_depot"] = sub_dtd

    # Extract vehicles
    depot_id = sub_depot["id"]
    sub_vehicles = [v for v in data["vehicles"] if v["depot_id"] == depot_id]

    # Extract constants
    sub_constants = data["constants"]

    # Reindex stations
    id = 0
    for st in sub_stations:
        st["id"] = id
        id += 1

    # Reindex depots
    id = 0
    for dp in sub_depots:
        orig_id = dp["id"]
        dp["id"] = id
        for v in sub_vehicles:
            if v["depot_id"] == orig_id:
                v["depot_id"] = id
        id += 1

    # Reindex vehicles
    id = 0
    for v in sub_vehicles:
        v["id"] = id
        id += 1

    # Export subproblem
    data_new = {
        "depots": sub_depots,
        "stations": sub_stations, 
        "distances": sub_distances, 
        "vehicles": sub_vehicles,
        "constants": sub_constants
    }

    with open(sub_instance, "w") as outfile:
        json.dump(data_new, outfile, indent=4)
        print("Exported instance", sub_instance)