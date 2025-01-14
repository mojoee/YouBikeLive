#!/usr/bin/env python3

import sys
import os

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(src_path)
sys.path.append(utils_path)

from split_delivery_utils import *
from tee import Tee
from createSolutionVisualization_v4 import visualize_solution

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
    "v4": rebalance_v4, 
    "v4_cb": rebalance_v4
}

unit_instance_generator_map = {
    "v1_1": generate_unit_instance_v1,
    "v1_2": generate_unit_instance_v1,
    "v1_2_minmax": generate_unit_instance_v1, 
    "v2_1_minmax": generate_unit_instance_v2,
    "v3_1_minmax":generate_unit_instance_v3,
    "v4": generate_unit_instance_v4, 
    "v4_cb": generate_cb_instance
}

suffix_map = {
    "v1_1": "_unit.json",
    "v1_2": "_unit.json",
    "v1_2_minmax": "_unit.json",
    "v2_1_minmax": "_unit.json",
    "v3_1_minmax": "_unit.json",
    "v4": "_unit.json",
    "v4_cb": "_cb.json"
}


def rebalance_unit(instance_path, solution_path, time_limit, remove, rebalancing_label):
    """
    Applies given rebalancing function to unit instance. 
    In effect achieving split loading and deliveries.
    """
    suffix = suffix_map[rebalancing_label]

    # 1) Generate unit instance
    unit_instance_path = instance_path.replace(".json", suffix)

    if os.path.exists(unit_instance_path):
        print("Unit instance already exists:", unit_instance_path)
    else:
        print("Generating unit instance:", unit_instance_path, " . . . ")
        unit_instance_generator = unit_instance_generator_map[rebalancing_label]
        unit_instance_generator(instance_path, unit_instance_path)

    # 2) Solve unit instance
    unit_solution_path = solution_path.replace(".json", suffix)
    rebalancing_function = rebalancing_map[rebalancing_label]
    rebalancing_function(unit_instance_path, unit_solution_path, time_limit)

    # 3) Process unit solution
    process_split_solution(unit_instance_path, unit_solution_path, solution_path)

    # 4) Clean mess
    if remove:
        os.remove(unit_instance_path)
        os.remove(unit_solution_path)
        print("Unit instance and solution removed.")




if __name__ == "__main__":
    # PARAMETERS
    instance_path = "./data/instances_v4/24-12-28.json"
    solution_dir = "./results/v4_cb/"
    time_limit = 30
    remove = False
    function_label = "v4_cb"

    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i':
            instance_path = sys.argv[i+1]
        elif sys.argv[i] == '-o':
            solution_dir = sys.argv[i+1]
        elif sys.argv[i] == '-t':
            time_limit = int(sys.argv[i+1])
        elif sys.argv[i] == '-r':
            remove = True
        elif sys.argv[i] == '-f':
            function_label = sys.argv[i+1]

    name = instance_path.split('/')[-1]
    solution_path = solution_dir + name
    os.makedirs(solution_dir, exist_ok=True)

    # Redirect stdout to log file
    problem_name = instance_path.split("/")[-1].replace(".json", "")
    log_file_path = solution_dir + problem_name + ".log"
    log_file = open(log_file_path, 'w')
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    rebalance_unit(instance_path, solution_path, time_limit, remove, function_label)

    # Visualize final solution
    save_path = solution_path.replace('.json', '.html')
    visualize_solution(instance_path, solution_path, save_path)
