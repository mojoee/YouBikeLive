#!/usr/bin/env python3

import os
import subprocess


PROBLEM_DIR = "./data/nX-30_v5-20/"
SOLUTION_DIR = "./results/nX-30_v5-20/"
CMD = "./optimization/models/rebalance_v1.py"
TIME_LIMIT = 2*60


if not os.path.exists(SOLUTION_DIR):
    os.makedirs(SOLUTION_DIR)

files = os.listdir(PROBLEM_DIR)

for file in files:
    instance = PROBLEM_DIR + file
    output = SOLUTION_DIR + file
    subprocess.run(['python3', CMD, '-i', instance, '-o', output, '-t', str(TIME_LIMIT)])