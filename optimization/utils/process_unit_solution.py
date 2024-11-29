#!/usr/bin/env python3

import json
import numpy as np
import sys

# PARAMETERS
instance_path = "./data/instances/demo_unit.json"
solution_path = "./results/demo_unit.json"

for i in range(len(sys.argv)):
    if sys.argv[i] == '-i':
        instance_path = sys.argv[i+1]
    elif sys.argv[i] == '-s':
        solution_path = sys.argv[i+1]

# LOAD
data = {}
with open(instance_path, 'r') as file:
    data = json.load(file)

solution = {}
with open(solution_path, 'r') as file:
    solution = json.load(file)

for rt in solution["routes"]:
    route = rt["route"]
    # route_parents = [data["stations"][node]["parent_id"] for node in route]
    # print(route_parents)
    loads = rt["leaving_load"]
    # print(loads)    
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
instance_path_orig = instance_path.replace("_unit.json", ".json")
solution["instance"] = instance_path_orig

solution_path_new = solution_path.replace("_unit.json", ".json")

with open(solution_path_new, "w") as outfile:
    json.dump(solution, outfile, indent=4)
    print("Exported solution", solution_path_new)