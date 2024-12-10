#!/usr/bin/env python3

import json
import numpy as np
import sys


def generate_unit_instance_v1(instance_path, output_path):
    # LOAD
    with open(instance_path, 'r') as file:
        data = json.load(file)

    # GENERATE UNIT INSTANCE
    # 1) Generate stations with unit demand
    stations_new = []
    stCnt_new = 0
    stations = data["stations"]
    for station in stations:
        demand = station["s_goal"] - station["s_init"]
        if demand == 0:
            continue
        demand_new = np.sign(demand)
        for i in range(abs(demand)):
            station_new = {"id": stCnt_new, "parent_id": station["id"]}
            stCnt_new += 1
            if demand_new > 0:
                station_new["s_init"] = 0
                station_new["s_goal"] = 1
            else:
                station_new["s_init"] = 1
                station_new["s_goal"] = 0
            stations_new.append(station_new)
    print("Generated stations_new")

    # 2) Generate distance matrix
    distances = data["distances"]
    distances_new = []
    for i in range(stCnt_new):
        distances_row = [None] * stCnt_new
        for j in range(stCnt_new):
            dist = distances[stations_new[i]["parent_id"]][stations_new[j]["parent_id"]]
            distances_row[j] = int(dist)
        distances_new.append(distances_row)
    print("Generated distances_new")

    # 3) Generate depot
    depot = data["depot"]
    depot_new = {}
    dfd_new = []
    dtd_new = []
    for station in stations_new:
        dfd_new.append(int(depot["dists_from_depot"][station["parent_id"]]))
        dtd_new.append(int(depot["dists_to_depot"][station["parent_id"]]))
    depot_new["dists_from_depot"] = dfd_new
    depot_new["dists_to_depot"] = dtd_new
    print("Generated depot_new")

    # 4) Carry over vehicles
    vehicles_new = data["vehicles"]

    # Export unit instance
    data_new = {
        "depot": depot_new,
        "stations": stations_new, 
        "distances": distances_new, 
        "vehicles": vehicles_new
    }
    print("data_new prepared")

    with open(output_path, "w") as outfile:
        json.dump(data_new, outfile, indent=None)
        print("Exported instance", output_path)

    return





def generate_unit_instance_v2(instance_path, output_path):
    # LOAD
    with open(instance_path, 'r') as file:
        data = json.load(file)

    # GENERATE UNIT INSTANCE
    # 1) Generate stations with unit demand
    stations_new = []
    stCnt_new = 0
    stations = data["stations"]
    for station in stations:
        demand = station["s_goal"] - station["s_init"]
        if demand == 0:
            continue
        demand_new = np.sign(demand)
        for i in range(abs(demand)):
            station_new = {"id": stCnt_new, "parent_id": station["id"]}
            stCnt_new += 1
            if demand_new > 0:
                station_new["s_init"] = 0
                station_new["s_goal"] = 1
            else:
                station_new["s_init"] = 1
                station_new["s_goal"] = 0
            stations_new.append(station_new)
    print("Generated stations_new")

    # 2) Generate distance matrix
    distances = data["distances"]
    distances_new = []
    for i in range(stCnt_new):
        distances_row = [None] * stCnt_new
        for j in range(stCnt_new):
            dist = distances[stations_new[i]["parent_id"]][stations_new[j]["parent_id"]]
            distances_row[j] = int(dist)
        distances_new.append(distances_row)
    print("Generated distances_new")

    # 3) Generate depot
    depots = data["depots"]
    depots_new = []
    for depot in depots:
        depot_new = depot
        dfd_new = []
        dtd_new = []
        for station in stations_new:
            dfd_new.append(int(depot["dists_from_depot"][station["parent_id"]]))
            dtd_new.append(int(depot["dists_to_depot"][station["parent_id"]]))
        depot_new["dists_from_depot"] = dfd_new
        depot_new["dists_to_depot"] = dtd_new
        depots_new.append(depot_new)
    print("Generated depot_new")

    # 4) Carry over vehicles
    vehicles_new = data["vehicles"]

    # Export unit instance
    data_new = {
        "depots": depots_new,
        "stations": stations_new, 
        "distances": distances_new, 
        "vehicles": vehicles_new
    }
    print("data_new prepared")

    with open(output_path, "w") as outfile:
        json.dump(data_new, outfile, indent=None)
        print("Exported instance", output_path)

    return


if __name__ == "__main__":
    instance_path = sys.argv[1]
    output_path = instance_path.replace(".json", "_unit.json")

    # generate_unit_instance_v1(instance_path, output_path)
    generate_unit_instance_v2(instance_path, output_path)