#!/usr/bin/env python3

import os
import sys
import json

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(src_path)
sys.path.append(utils_path)

from rebalance_v4 import rebalance_v4
from split_delivery_utils import *
from createSolutionVisualization_v4 import visualize_solution
from tee import Tee




def rebalance_v4_ws(instance, solution_dir, time_limit_init, time_limit_unit):
    os.makedirs(solution_dir, exist_ok=True)

    problem_name = instance.split("/")[-1].replace(".json", "")
    instance_dir = instance.rsplit("/", 1)[0] + "/"

    # Redirect stdout to log file
    log_file_path = solution_dir + problem_name + ".log"
    log_file = open(log_file_path, 'w')
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    # Solve original instance
    solution_init = solution_dir + problem_name + "_init.json"
    rebalance_v4(instance, solution_init, time_limit_init) if not os.path.exists(solution_init) else print(f"solution_init already exists: {solution_init}")        

    # Create initial solution visualization
    save_path = solution_init.replace('.json', '.html')
    visualize_solution(instance, solution_init, save_path)

    # Generate unit instance
    instance_unit = instance_dir + problem_name + "_unit.json"
    generate_unit_instance_v4(instance, instance_unit) if not os.path.exists(instance_unit) else print(f"instance_unit already exists: {instance_unit}")        

    # Generate initial unit routes
    routes_init = generate_init_unit_routes(instance_unit, solution_init)

    # Solve unit instance with warm start
    solution_unit = solution_dir + problem_name + "_unit.json"
    rebalance_v4(instance_unit, solution_unit, time_limit_unit, routes_init) if not os.path.exists(solution_unit) else print(f"solution_unit already exists: {solution_unit}")

    # Process unit solution
    solution = solution_dir + problem_name + ".json"
    process_split_solution(instance_unit, solution_unit, solution)

    # Create final solution visualization
    save_path = solution.replace('.json', '.html')
    visualize_solution(instance, solution, save_path)




if __name__ == "__main__":
    instance = "./data/instances_v4/v12-24-24_b8h_d12/NTU.json"
    solution_dir = "./results/v4_ws/v12-24-24_b8h_d12/NTU/"
    time_limit_init = 10
    time_limit_unit = 10

    rebalance_v4_ws(instance, solution_dir, time_limit_init, time_limit_unit)

