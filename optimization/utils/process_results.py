#!/usr/bin/env python3

import os
import json
import re
from tabulate import tabulate
import numpy as np


is_mapping = {"proportional": "prop",
              "duration": "dur",
              "peak": "peak"
              }



def get_makespan_lb(file):
    with open(file, "r") as f:
        data = json.load(f)
    return int(data["objectives"][1]["value"] / 60)


def get_t_max_reward(log_file, max_reward):
    with open(log_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip("\[ \]")
            words = line.split()
            if len(words) == 7 and words[1] == "sec,":
                t = int(words[0])
                reward = int(words[4])
                makespan = int(int(words[6]) / 60)
                if reward == max_reward:
                    return t, makespan
    return float('nan'), float('nan')

results_dir = "./results/v4_cb/naive_21/proportional/"
results_dir = "./results/v4_unit/naive_21/"
results_dir = "./results/v4_cbws/naive_21/"
results_dir = "./results/v4_cb/naive_21/duration/"
results_dir = "./results/v4_cb/naive_21/peak/"


v5_results_dir = "./results/v5/naive_21/"

table_data = []

for file in sorted(os.listdir(results_dir)):
# for file in ["naive_2025-01-02_proportional.json"]:
    if file.endswith(".json"):
        with open(results_dir + file, "r") as f:
            data = json.load(f)
            match = re.search(r'(\d{4}-\d{2}-\d{2})[^_]*_(\w+)\.json$', file)

            if match:
                date = match.group(1)
                last_word = is_mapping[match.group(2)]
            else:
                date = "unknown"
                last_word = "unknown"

            max_reward = int(data["abs_demands_total"])

            v5_sol_file = v5_results_dir + file
            makespan_lb = get_makespan_lb(v5_sol_file)

            reward = data["objectives"][0]["value"]
            reward_rel = reward / max_reward * 100

            makespan = int(data["objectives"][1]["value"]/60)
            makespan_gap = ((makespan - makespan_lb) / makespan_lb) * 100

            log_file = results_dir + file.replace(".json", ".txt")
            t_first, makespan_first = get_t_max_reward(log_file, max_reward)
            makespan_first_gap = ((makespan_first - makespan_lb) / makespan_lb) * 100

            table_data.append([f"{date}_{last_word}", max_reward, makespan_lb, reward, reward_rel, makespan, makespan_gap, t_first, makespan_first_gap])

# Calculate averages for each column
averages = ["mean"]
for col in range(1, len(table_data[0])):
    col_values = [row[col] for row in table_data if not np.isnan(row[col])]
    averages.append(np.mean(col_values))

# Append averages to table_data
table_data.append(averages)

# Generate LaTeX table with int and float formats
headers = ["Instance", "Max Reward", "Makespan LB", "Reward", "Reward Rel (%)", "Makespan", "Makespan Gap (%)", "T First", "Makespan First Gap (%)"]
floatfmts = (".0f", ".0f", ".0f", ".0f", ".2f", ".0f", ".2f", ".0f", ".2f")
latex_table = tabulate(table_data, headers, tablefmt="latex", floatfmt=floatfmts)

# Print LaTeX table
print(latex_table)