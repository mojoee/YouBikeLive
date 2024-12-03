#!/usr/bin/env python3

import sys
import os

from generate_unit_instance import generate_unit_instance

# PARAMETERS
instance_path = "./data/instances/demo.json"
solution_path = "./demo.json"
time_limit = 5

for i in range(len(sys.argv)):
    if sys.argv[i] == '-i':
        instance_path = sys.argv[i+1]
    elif sys.argv[i] == '-o':
        solution_path = sys.argv[i+1]
    elif sys.argv[i] == '-t':
        time_limit = int(sys.argv[i+1])

# 1) Generate unit instance
unit_instance_path = instance_path.replace(".json", "_unit.json")

if os.path.exists(unit_instance_path):
    print("Unit instance already exists:", unit_instance_path)
else:
    print("Generating unit instance:", unit_instance_path, " . . . ")
    generate_unit_instance(instance_path, unit_instance_path)

# 2) Solve unit instance TODO

# 3) Process unit solution TODO

# 4) Clean mess