#!/usr/bin/env python3

import os
import subprocess

PROBLEM_DIR = "./data/nX-30_v5-20/"
SOLUTION_DIR = "./results/nX-30_v5-20/"
CMD = "./optimization/utils/checker_v1.py"

files = os.listdir(PROBLEM_DIR)

for file in files:
    instance = PROBLEM_DIR + file
    output = SOLUTION_DIR + file
    subprocess.run(['python3', CMD, '-i', instance, '-o', output])
