#!/usr/bin/env python3

import hexaly.optimizer
import sys
import json
import os




def rebalance_v4(instance_path, solution_path, time_limit):
    """
    1) Maximize cumulative reward for rebalancing.
    Limited trip duration = travel time + loading time * parking time.
    Everyone visited and served exactly once.
    Considers multiple depots and vehicles with different capacities.
    """

        # LOAD DATA
    with open(instance_path, 'r') as file:
        data = json.load(file)

    data["stations"].sort(key = lambda x:x["id"])
    data["depots"].sort(key = lambda x:x["id"])
    data["vehicles"].sort(key = lambda x:x["id"])

    stations_cnt = len(data["stations"])
    demands_data = [station["s_goal"] - station["s_init"] for station in data["stations"]]
    rewards_data = [station["c_reward"] for station in data["stations"]]
    stations_parents_data = []
    if "parent_id" in data["stations"][0]:
        stations_parents_data = [st["parent_id"] for st in data["stations"]]
    else:
        stations_parents_data = [i for i in range(stations_cnt)]

    dist_matrix_data = data["distances"]
    
    vehicles_cnt = len(data["vehicles"])
    vehicles_capacities = [v["capacity"] for v in data["vehicles"]]
    vehicles_depots = [v["depot_id"] for v in data["vehicles"]]
    
    depots_cnt = len(data["depots"])
    dist_from_depots_data = [d["dists_from_depot"] for d in data["depots"]]
    dist_to_depots_data = [d["dists_to_depot"] for d in data["depots"]]
    
    parking_time = data["constants"]["parking_time"]
    loading_time = data["constants"]["loading_time"]
    max_trip_duration = data["constants"]["max_trip_duration"]

    print("Solving", instance_path)
    print("stations_cnt:", stations_cnt)
    print("demand_min:", min(demands_data))
    print("demand_max", max(demands_data))
    print("demands", demands_data)
    print("vehicles_cnt:", vehicles_cnt)
    print("vehicles_capacities:", vehicles_capacities)
    print("vehicles_depots", vehicles_depots)
    print("depots_cnt:", depots_cnt)
    print("parking_time:", parking_time)
    print("loading_time:", loading_time)
    print("max_trip_duration:", max_trip_duration)
    print()

        # MODEL
    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model

        # Create Hexaly arrays to be able to access them with an "at" operator
        demands = model.array(demands_data)
        rewards = model.array(rewards_data)
        dist_matrix = model.array(dist_matrix_data)
        dist_from_depots = [model.array(d) for d in dist_from_depots_data]
        dist_to_depots = [model.array(d) for d in dist_to_depots_data]
        stations_parents = model.array(stations_parents_data)

        # DECISION VARIABLES 
        routes = [model.list(stations_cnt) for _ in range(vehicles_cnt)] # Sequence of stations visited by each vehicle

        # INTERMEDIATE EXPRESSIONS
        loads = [None] * vehicles_cnt # current vehicle loads at each station
        routes_costs = [None] * vehicles_cnt
        routes_rewards = [None] * vehicles_cnt

        # CONSTRAINT 1
        model.constraint(model.disjoint(routes)) # All customers must be visited at most once

        for k in range(vehicles_cnt):
            route = routes[k]
            c = model.count(route)

            # Leaving load at each station visited by vehicle k
            load_lambda = model.lambda_function(lambda i, prev: prev - demands[route[i]])
            loads[k] = model.array(model.range(0, c), load_lambda, 0)

            # Constraint on min and max vehicle capacity
            max_quantity_lambda = model.lambda_function(lambda i: loads[k][i] <= vehicles_capacities[k])
            model.constraint(model.and_(model.range(0, c), max_quantity_lambda))

            min_quantity_lambda = model.lambda_function(lambda i: loads[k][i] >= 0)
            model.constraint(model.and_(model.range(0, c), min_quantity_lambda))

            # Distance traveled by each vehicle
            dist_lambda = model.lambda_function(lambda i: model.at(dist_matrix, route[i - 1], route[i]))
            depot_id = vehicles_depots[k]
            travel_cost = model.sum(model.range(1, c), dist_lambda) + model.iif(c > 0, dist_from_depots[depot_id][route[0]] + dist_to_depots[depot_id][route[c - 1]], 0)

            loading_lambda = model.lambda_function(lambda i: loading_time * abs(model.at(demands, route[i])))
            loading_cost = model.sum(model.range(0, c), loading_lambda)

            parking_lambda = model.lambda_function(lambda i: parking_time * (model.at(stations_parents, route[i - 1]) != model.at(stations_parents, route[i])))
            parking_cost = model.sum(model.range(1, c), parking_lambda) + model.iif(c > 0, parking_time, 0)

            routes_costs[k] = travel_cost + loading_cost + parking_cost

            reward_lambda = model.lambda_function(lambda i: model.at(rewards, route[i]) * abs(model.at(demands, route[i])))
            routes_rewards[k] = model.sum(model.range(0, c), reward_lambda)

            # Contraint on total trip duration
            model.constraint(routes_costs[k] <= max_trip_duration)

        # OBJECTIVES
        # 1) Maximize cumulative reward
        total_reward = model.sum(routes_rewards)
        model.maximize(total_reward)
        # 2) Minimize total trip duration
        max_duration = model.max(routes_costs)
        model.minimize(max_duration)

        model.close()

        # SOLVE
        optimizer.param.time_limit = time_limit
        optimizer.solve()

        # OUTPUT
        result = {}
        
        sol = optimizer.get_solution()

        result["instance"] = instance_path
        result["time_limit"] = optimizer.param.time_limit
        result["running_time"] = optimizer.get_statistics().get_running_time()
        result["status"] = str(sol.get_status()).replace('HxSolutionStatus.', '')
        result["objectives"] = [
            {"name": "total_reward", "value": sol.get_value(total_reward), "bound": sol.get_objective_bound(0), "gap": sol.get_objective_gap(0)},
            {"name": "max_duration", "value": sol.get_value(max_duration), "bound": sol.get_objective_bound(1), "gap": sol.get_objective_gap(1)}
            ]
        result["routes"] = []
        for k in range(vehicles_cnt):
            route = [station for station in routes[k].value]
            leaving_load = [load for load in loads[k].value]
            result["routes"].append({"reward": routes_rewards[k].value, "duration": routes_costs[k].value, "route": route, "leaving_load": leaving_load})        
        result_string = json.dumps(result, indent=4)

        with open(solution_path, "w") as outfile:
            outfile.write(result_string)
            print("Solution exported to", solution_path)




if __name__ == "__main__":
    # DEFAULT PARAMETERS
    instance_path = "./data/instances_v4/n10_v4_d2.json"
    solution_dir = "./results/v4/"
    time_limit = 30

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

    rebalance_v4(instance_path, solution_path, time_limit)