#!/usr/bin/env python3

import json
import numpy as np



def generate_init_unit_routes(instance_unit, solution_init):
    """
    Given an instance_unit and a solution_init to original instance, generate the initial routes for the instance_unit.
    """

    # Get station mapping: parent_id in instance -> list of child ids in instance_unit
    instance_unit_data = json.load(open(instance_unit))
    station_mapping = {} 
    for st in instance_unit_data["stations"]:
        parent_id = st["parent_id"]
        if parent_id not in station_mapping:
            station_mapping[parent_id] = [st["id"]]
        else: 
            station_mapping[parent_id].append(st["id"])

    # Get solution_init data
    solution_init_data = json.load(open(solution_init))
    routes_init = []
    for rd in solution_init_data["routes"]:
        route_init = []

        el = 0 # entry load
        for st, ll in zip(rd["route"], rd["leaving_load"]): # station, leaving load
            ld = abs(ll - el) # load difference
            el = ll
            popped_nodes = station_mapping[st][:ld]
            del station_mapping[st][:ld]
            route_init.extend(popped_nodes)
        routes_init.append(route_init)
    return routes_init




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




def generate_unit_instance_v3(instance_path, output_path):
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

    # 4) Carry over vehicles and constants
    vehicles_new = data["vehicles"]
    constants_new = data["constants"]

    # Export unit instance
    data_new = {
        "depots": depots_new,
        "stations": stations_new, 
        "distances": distances_new, 
        "vehicles": vehicles_new,
        "constants": constants_new
    }
    print("data_new prepared")

    with open(output_path, "w") as outfile:
        json.dump(data_new, outfile, indent=None)
        print("Exported instance", output_path)

    return




def generate_unit_instance_v4(instance_path, output_path):
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
            station_new = {"id": stCnt_new, "parent_id": station["id"], "c_reward": station["c_reward"]}
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

    # 4) Carry over vehicles and constants
    vehicles_new = data["vehicles"]
    constants_new = data["constants"]

    # Export unit instance
    data_new = {
        "depots": depots_new,
        "stations": stations_new, 
        "distances": distances_new, 
        "vehicles": vehicles_new,
        "constants": constants_new
    }
    print("data_new prepared")

    with open(output_path, "w") as outfile:
        json.dump(data_new, outfile, indent=None)
        print("Exported instance", output_path)

    return




def generate_cb_instance(instance_path, output_path):
    """
    Generate a capacity-bounded instance.
    """

    # LOAD
    with open(instance_path, 'r') as file:
        data = json.load(file)

    # GENERATE CAPACITY-BOUNDED INSTANCE
    # 1) Determine the smallest vehicle capacity
    vehicles = data["vehicles"]
    min_capacity = min(vehicle["capacity"] for vehicle in vehicles)

    # 2) Generate stations with capacity-bounded demand
    stations_new = []
    stCnt_new = 0
    stations = data["stations"]
    for station in stations:
        demand = station["s_goal"] - station["s_init"]
        if demand == 0:
            continue
        demand_new = np.sign(demand)
        for i in range(abs(demand) // min_capacity):
            station_new = {"id": stCnt_new, "parent_id": station["id"], "c_reward": station["c_reward"]}
            stCnt_new += 1
            if demand_new > 0:
                station_new["s_init"] = 0
                station_new["s_goal"] = min_capacity
            else:
                station_new["s_init"] = min_capacity
                station_new["s_goal"] = 0
            stations_new.append(station_new)
        remaining_demand = abs(demand) % min_capacity
        if remaining_demand > 0:
            station_new = {"id": stCnt_new, "parent_id": station["id"], "c_reward": station["c_reward"]}
            stCnt_new += 1
            if demand_new > 0:
                station_new["s_init"] = 0
                station_new["s_goal"] = remaining_demand
            else:
                station_new["s_init"] = remaining_demand
                station_new["s_goal"] = 0
            stations_new.append(station_new)
    print("Generated stations_new")

    # 3) Generate distance matrix
    distances = data["distances"]
    distances_new = []
    for i in range(stCnt_new):
        distances_row = [None] * stCnt_new
        for j in range(stCnt_new):
            dist = distances[stations_new[i]["parent_id"]][stations_new[j]["parent_id"]]
            distances_row[j] = int(dist)
        distances_new.append(distances_row)
    print("Generated distances_new")

    # 4) Generate depot
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

    # 5) Carry over vehicles and constants
    vehicles_new = data["vehicles"]
    constants_new = data["constants"]

    # Export capacity-bounded instance
    data_new = {
        "depots": depots_new,
        "stations": stations_new, 
        "distances": distances_new, 
        "vehicles": vehicles_new,
        "constants": constants_new
    }
    print("data_new prepared")

    with open(output_path, "w") as outfile:
        json.dump(data_new, outfile, indent=None if stCnt_new > 200 else 4)
        print("Exported instance", output_path)
    return




def process_split_solution(instance, solution_split, solution_out):
    # LOAD
    data = {}
    with open(instance, 'r') as file:
        data = json.load(file)

    solution = {}
    with open(solution_split, 'r') as file:
        solution = json.load(file)

    for rt in solution["routes"]:
        route = rt["route"]
        # route_parents = [data["stations"][node]["parent_id"] for node in route]
        # print(route_parents)
        loads = rt["leaving_load"]
        # print(loads)    
        route_merged = []
        loads_merged = []
        if len(route) > 0:
            route_merged = [data["stations"][route.pop()]["parent_id"]]
            loads_merged = [loads.pop()]
            while(len(route) > 0):
                node = route.pop()
                load = loads.pop()
                node_parent = data["stations"][node]["parent_id"]
                if route_merged[-1] != node_parent:
                    route_merged.append(node_parent)
                    loads_merged.append(load)
            route_merged.reverse()
            loads_merged.reverse()
            # print(route_merged)
            # print(loads_merged)
        rt["route"] = route_merged
        rt["leaving_load"] = loads_merged


    # Export
    solution["instance"] = instance
    with open(solution_out, "w") as outfile:
        json.dump(solution, outfile, indent=4)
        print("Unit solution processed, exported", solution_out)




if __name__ == "__main__":
    instance_path = "data/instances_v4/v12-24-24_b8h_d12/NTU.json"
    output_path = instance_path.replace(".json", "_cb.json")    
    generate_cb_instance(instance_path, output_path)

    instance_path = "data/instances_v4/v12-24-24_b8h_d12/NTU.json"
    output_path = instance_path.replace(".json", "_unit.json")
    # generate_unit_instance_v1(instance_path, output_path)
    # generate_unit_instance_v2(instance_path, output_path)
    # generate_unit_instance_v3(instance_path, output_path)
    generate_unit_instance_v4(instance_path, output_path)

    instance_path = "./data/instances_v4/v12-24-24_b8h_d12/NTU_unit.json"
    solution_path_split = "./results/unit_v4/v12-24-24_b8h_d12/NTU_unit.json"
    solution_path = solution_path_split.replace("_unit.json", ".json")
    process_split_solution(instance_path, solution_path_split, solution_path)