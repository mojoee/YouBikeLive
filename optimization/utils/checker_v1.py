#!/usr/bin/env python3

import sys
import json
from pytest import approx
from colorama import Fore

# PARAMETERS
instance_path = "./data/demo.json"
solution_path = "./results/demo.json"

for i in range(len(sys.argv)):
    if sys.argv[i] == '-i':
        instance_path = sys.argv[i+1]
    elif sys.argv[i] == '-o':
        solution_path = sys.argv[i+1]

print("*** SOLUTION VALIDITY CHECK ***")
print("Instance:", instance_path)
print("Solution:", solution_path)


# LOAD
with open(instance_path, 'r') as file:
    instance_data = json.load(file)

with open(solution_path, 'r') as file:
    solution_data = json.load(file)



routes = solution_data["routes"]

# routes_cnt <= vehicles_cnt
c1 = len(routes) <= instance_data["vehicles"]["count"]
print("routes_cnt <= vehicles_cnt:\t", c1)

# route checks
c2 = True # vehicle capacity
c3 = True # reported load calculation
for route_data in routes:
    route = route_data["route"]
    loads = route_data["leaving_load"]
    load_ = 0
    for v, load in zip(route, loads):
        demand = instance_data["stations"][v]["s_goal"] - instance_data["stations"][v]["s_init"]
        load_ -= demand
        c2 = c2 and load <= instance_data["vehicles"]["capacity"]
        c3 = c3 and load_ == load

print("load <= vehicle_capacity:\t", c2)
print("load_reported == load_actual:\t", c3)

# distance calculation 
total_distance = 0 # total distance calculation
for route_data in routes:
    distance = 0
    route = route_data["route"]
    distance += instance_data["depot"]["dists_from_depot"][route[0]]
    distance += instance_data["depot"]["dists_to_depot"][route[-1]]
    for i in range(len(route) - 1):
        v_from = route[i]
        v_to = route[i+1]
        distance += instance_data["distances"][v_from][v_to]
    total_distance += distance
c4 = total_distance == approx(solution_data["objectives"][1]["value"])
print("dist_reported == dist_actual:\t", c4)

# Every station served once
stations_cnt = len(instance_data["stations"])
routes_merged = []
for route_data in routes:
    route = route_data["route"]
    routes_merged.extend(route)
s = set(routes_merged)
c5 = stations_cnt == len(s)
c6 = stations_cnt == len(routes_merged)
print("All stations served:\t\t", c5)
print("All stations served ex. once:\t", c6)

# All tests eval.
res = c1 and c2 and c3 and c4 and c5 and c6
if res:
    print(Fore.GREEN + 'All tests passed!')
else:
    print(Fore.RED + 'Some tests failed!')
print(Fore.WHITE)