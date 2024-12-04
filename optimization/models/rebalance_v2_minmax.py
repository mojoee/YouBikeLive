#!/usr/bin/env python3

import sys
import os

from generate_unit_instance import generate_unit_instance
from process_unit_solution import process_unit_solution
from rebalance_v1_2_minmax import rebalance_v1_2_minmax




def rebalance_v2_minmax(instance_path, solution_path, time_limit, remove):
    """
    1) minimize max distance by a singe vehicle
    Always use all vehicles.
    Split loading and deliveries.
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
    rebalance_v1_2_minmax(unit_instance_path, unit_solution_path, time_limit)

    # 3) Process unit solution
    process_unit_solution(unit_instance_path, unit_solution_path)

    # 4) Clean mess
    if remove:
        os.remove(unit_instance_path)
        os.remove(unit_solution_path)
        print("Unit instance and solution removed.")




if __name__ == "__main__":
    # PARAMETERS
    instance_path = "./data/instances/demo.json"
    solution_path = "./demo.json"
    time_limit = 5
    remove = False

    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i':
            instance_path = sys.argv[i+1]
        elif sys.argv[i] == '-o':
            solution_path = sys.argv[i+1]
        elif sys.argv[i] == '-t':
            time_limit = int(sys.argv[i+1])
        elif sys.argv[i] == '-r':
            remove = True
