#!/usr/bin/env python3

import sys
import os

from generate_unit_instance import generate_unit_instance_v1, generate_unit_instance_v2, generate_unit_instance_v3, generate_unit_instance_v4
from process_unit_solution import process_unit_solution

# Different rebalancing functions
from rebalance_v1_1 import rebalance_v1_1
from rebalance_v1_2 import rebalance_v1_2
from rebalance_v1_2_minmax import rebalance_v1_2_minmax
from rebalance_v2_1_minmax import rebalance_v2_1_minmax
from rebalance_v3_1_minmax import rebalance_v3_1_minmax
from rebalance_v4 import rebalance_v4

rebalancing_map = {
    "v1_1": rebalance_v1_1,
    "v1_2": rebalance_v1_2,
    "v1_2_minmax": rebalance_v1_2_minmax,
    "v2_1_minmax": rebalance_v2_1_minmax,
    "v3_1_minmax": rebalance_v3_1_minmax,
    "v4": rebalance_v4
}

unit_instance_generator_map = {
    "v1_1": generate_unit_instance_v1,
    "v1_2": generate_unit_instance_v1,
    "v1_2_minmax": generate_unit_instance_v1, 
    "v2_1_minmax": generate_unit_instance_v2,
    "v3_1_minmax":generate_unit_instance_v3,
    "v4": generate_unit_instance_v4
}


def rebalance_unit(instance_path, solution_path, time_limit, remove, rebalancing_label):
    """
    Applies given rebalancing function to unit instance. 
    In effect achieving split loading and deliveries.
    """

    # 1) Generate unit instance
    unit_instance_path = instance_path.replace(".json", "_unit.json")

    if os.path.exists(unit_instance_path):
        print("Unit instance already exists:", unit_instance_path)
    else:
        print("Generating unit instance:", unit_instance_path, " . . . ")
        unit_instance_generator = unit_instance_generator_map[rebalancing_label]
        unit_instance_generator(instance_path, unit_instance_path)

    # 2) Solve unit instance
    unit_solution_path = solution_path.replace(".json", "_unit.json")
    rebalancing_function = rebalancing_map[rebalancing_label]
    rebalancing_function(unit_instance_path, unit_solution_path, time_limit)

    # 3) Process unit solution
    process_unit_solution(unit_instance_path, unit_solution_path)

    # 4) Clean mess
    if remove:
        os.remove(unit_instance_path)
        os.remove(unit_solution_path)
        print("Unit instance and solution removed.")




if __name__ == "__main__":
    # PARAMETERS
    instance_path = "./data/instances_v4/v12-24-24_b8h_d12.json"
    solution_dir = "./results/unit_v4/"
    time_limit = 300
    remove = False
    function_label = "v4"

    name = instance_path.split('/')[-1]
    solution_path = solution_dir + name
    os.makedirs(solution_dir, exist_ok=True)

    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i':
            instance_path = sys.argv[i+1]
        elif sys.argv[i] == '-o':
            solution_path = sys.argv[i+1]
        elif sys.argv[i] == '-t':
            time_limit = int(sys.argv[i+1])
        elif sys.argv[i] == '-r':
            remove = True
        elif sys.argv[i] == '-f':
            function_label = sys.argv[i+1]

    rebalance_unit(instance_path, solution_path, time_limit, remove, function_label)

# python3 ./optimization/models/rebalance_unit.py -i data/instances_v1/instance_test_12:30_v5_c20.json -o ./results/unit_v1-1/instance_test_12:30_v5_c20_1min.json -t 60 -f v1_1