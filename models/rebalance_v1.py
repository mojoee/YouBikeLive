#!/usr/bin/env python3

import hexaly.optimizer
import sys
import json


# Load instance
path = sys.argv[1]

with open(path, 'r') as file:
    data = json.load(file)

stations_cnt = len(data["stations"])
demands_data = [station["s_goal"] - station["s_init"] for station in data["stations"]]
vehicles_cnt = data["vehicles"]["count"]
vehicles_capacity = data["vehicles"]["capacity"]
dist_matrix_data = data["distances"]
dist_from_depot_data = data["depot"]["dists_from_depot"]
dist_to_depot_data = data["depot"]["dists_to_depot"]



# MODEL
with hexaly.optimizer.HexalyOptimizer() as optimizer:
    model = optimizer.model
    # Create Hexaly arrays to be able to access them with an "at" operator
    demands = model.array(demands_data)
    dist_matrix = model.array(dist_matrix_data)
    dist_from_depot = model.array(dist_from_depot_data)
    dist_to_depot = model.array(dist_to_depot_data)

    # DECISION VARIABLES 
    routes = [model.list(stations_cnt) for _ in range(vehicles_cnt)] # Sequence of stations visited by each vehicle
    loads = [None] * vehicles_cnt # current vehicle loads at each station

    # CONSTRAINTS
    # All customers must be visited by exactly one vehicle
    model.constraint(model.partition(routes))

    # A vehicle is used if it visits at least one customer
    vehicles_used = [(model.count(routes[k]) > 0) for k in range(vehicles_cnt)]

    routes_lens = [None] * vehicles_cnt
    for k in range(vehicles_cnt):
        route = routes[k]
        c = model.count(route)

        # Vehicle loads must be non-negative and within vehicle capacity at all times
        demand_lambda = model.lambda_function(lambda i, prev: prev - demands[route[i]])
        loads[k] = model.array(model.range(0, c), demand_lambda, 0)

        # Constraint on min and max vehicle capacity
        max_quantity_lambda = model.lambda_function(lambda i: loads[k][i] <= vehicles_capacity)
        model.constraint(model.and_(model.range(0, c), max_quantity_lambda))

        min_quantity_lambda = model.lambda_function(lambda i: loads[k][i] >= 0)
        model.constraint(model.and_(model.range(0, c), min_quantity_lambda))

        # Distance traveled by each vehicle
        dist_lambda = model.lambda_function(lambda i: model.at(dist_matrix, route[i - 1], route[i]))
        routes_lens[k] = model.sum(model.range(1, c), dist_lambda) + model.iif(c > 0, dist_from_depot[route[0]] + dist_to_depot[route[c - 1]], 0)

    # OBJECTIVES
    # Total number of vehicles
    vehicles_used_cnt = model.sum(vehicles_used)

    # Total distance traveled
    total_distance = model.sum(routes_lens)

    # Objective: minimize the number of vehicles used, then minimize the distance traveled
    model.minimize(vehicles_used_cnt)
    model.minimize(total_distance)
    model.close()

    # SOLVE
    optimizer.param.time_limit = 5
    optimizer.solve()

    # TODO output
    for k in range(vehicles_cnt):
        used = vehicles_used[k].value
        print("Vehicle %i used: %i" % (k, used))
        if used:
            for customer in routes[k].value:
                print(customer, end=" ")
            print()
            for load in loads[k].value:
                print(load, end=" ")
            print()
    