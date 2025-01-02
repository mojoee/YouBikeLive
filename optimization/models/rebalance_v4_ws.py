#!/usr/bin/env python3

import os
import sys
import json

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(src_path)
sys.path.append(utils_path)


from rebalance_v4 import rebalance_v4
from generate_unit_instance import generate_unit_instance_v4
from process_unit_solution import process_split_solution
from createSolutionVisualization_v4 import visualize_solution
from tee import Tee


instance = "./data/instances_v4/v12-24-24_b8h_d12/NTU.json"
solution_dir = "./results/ws_v4/v12-24-24_b8h_d12/"
time_limit_init = 30
time_limit_unit = 30

os.makedirs(solution_dir, exist_ok=True)
problem_name = instance.split("/")[-1].replace(".json", "")

log_file_path = solution_dir + problem_name + ".log"

# Redirect stdout to log file
sys.stdout = Tee(sys.stdout, open(log_file_path, 'w'))


# SOLVE ORIGINAL INSTANCE WITHOUT LOAD SPLITTING
solution_init = solution_dir + problem_name + "_init.json"
if os.path.exists(solution_init):
    print(f"solution_init already exists: {solution_init}")
else:
    rebalance_v4(instance, solution_init, time_limit_init)

# Create final solution visualization
save_path = solution_init.replace('.json', '.html')
visualize_solution(instance, solution_init, save_path)

# GENERATE UNIT INSTANCE
instance_dir = instance.rsplit("/", 1)[0] + "/"
instance_unit = instance_dir + problem_name + "_unit.json"
if os.path.exists(instance_unit):
    print(f"instance_unit already exists: {instance_unit}")
else:
    generate_unit_instance_v4(instance, instance_unit)

# SOLVE UNIT INSTANCE WARM STARTED WITH solution_init
solution_unit = solution_dir + problem_name + "_unit.json"

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
    for st in rd["route"]:
        route_init.extend(station_mapping[st])
    routes_init.append(route_init)

# Solve unit instance with warm start
if os.path.exists(solution_unit):
    print(f"solution_unit already exists: {solution_unit}")
else:
    rebalance_v4(instance_unit, solution_unit, time_limit_unit, routes_init)

# Process unit solution
solution = solution_dir + problem_name + ".json"
process_split_solution(instance_unit, solution_unit, solution)

# Create final solution visualization
save_path = solution.replace('.json', '.html')
visualize_solution(instance, solution, save_path)