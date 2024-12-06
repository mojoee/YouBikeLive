#!/usr/bin/env python3

import sys
import os

from generate_unit_instance import generate_unit_instance
from process_unit_solution import process_unit_solution

# Different rebalancing functions
from rebalance_v1_1 import rebalance_v1_1
from rebalance_v1_2 import rebalance_v1_2
from rebalance_v1_2_minmax import rebalance_v1_2_minmax




def rebalance_unit(instance_path, solution_path, time_limit, remove, rebalancing_function):
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
        generate_unit_instance(instance_path, unit_instance_path)

    # 2) Solve unit instance
    unit_solution_path = solution_path.replace(".json", "_unit.json")
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
    instance_path = "./data/instances_v1/demo.json"
    solution_path = "./results/demo.json"
    time_limit = 5
    remove = False
    function_label = "v1_1"

    function_map = {
        "v1_1": rebalance_v1_1,
        "v1_2": rebalance_v1_2,
        "v1_2_minmax": rebalance_v1_2_minmax
    }

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
    rebalancing_function = function_map[function_label]

    rebalance_unit(instance_path, solution_path, time_limit, remove, rebalancing_function)

# python3 ./optimization/models/rebalance_unit.py -i data/instances_v1/instance_test_12:30_v5_c20.json -o ./results/unit_v1-1/instance_test_12:30_v5_c20_1min.json -t 60 -f v1_1