#!/usr/bin/env python3

import hexaly.optimizer
import sys
import json




def rebalance_v2_1_minmax(instance_path, solution_path, time_limit):
    """
    1) minimize max distance by a singe vehicle
    Always use all vehicles.
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
    dist_matrix_data = data["distances"]
    vehicles_cnt = len(data["vehicles"])
    vehicles_capacities = [v["capacity"] for v in data["vehicles"]]
    vehicles_depots = [v["depot_id"] for v in data["vehicles"]]
    depots_cnt = len(data["depots"])
    dist_from_depots_data = [d["dists_from_depot"] for d in data["depots"]]
    dist_to_depots_data = [d["dists_to_depot"] for d in data["depots"]]

    print("Solving", instance_path)
    print("stations_cnt:", stations_cnt)
    print("demand_min:", min(demands_data))
    print("demand_max", max(demands_data))
    print("vehicles_cnt:", vehicles_cnt)
    print("vehicles_capacities:", vehicles_capacities)
    print("vehicles_depots", vehicles_depots)
    print("depots_cnt:", depots_cnt)
    print()

    # MODEL
    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model

        # Create Hexaly arrays to be able to access them with an "at" operator
        demands = model.array(demands_data)
        dist_matrix = model.array(dist_matrix_data)
        dist_from_depots = [model.array(d) for d in dist_from_depots_data]
        dist_to_depots = [model.array(d) for d in dist_to_depots_data]

        # DECISION VARIABLES 
        routes = [model.list(stations_cnt) for _ in range(vehicles_cnt)] # Sequence of stations visited by each vehicle

        # INTERMEDIATE EXPRESSIONS
        loads = [None] * vehicles_cnt # current vehicle loads at each station
        vehicles_used = [(model.count(routes[k]) > 0) for k in range(vehicles_cnt)] # A vehicle is used if it visits at least one customer
        routes_lens = [None] * vehicles_cnt

        # CONSTRAINT 1
        model.constraint(model.partition(routes)) # All customers must be visited by exactly one vehicle

        for k in range(vehicles_cnt):
            route = routes[k]
            c = model.count(route)

            # Leaving load at each station visited by vehicle k
            demand_lambda = model.lambda_function(lambda i, prev: prev - demands[route[i]])
            loads[k] = model.array(model.range(0, c), demand_lambda, 0)

            # Constraint on min and max vehicle capacity
            max_quantity_lambda = model.lambda_function(lambda i: loads[k][i] <= vehicles_capacities[k])
            min_quantity_lambda = model.lambda_function(lambda i: loads[k][i] >= 0)
            model.constraint(model.and_(model.range(0, c), max_quantity_lambda))
            model.constraint(model.and_(model.range(0, c), min_quantity_lambda))

            # Distance traveled by each vehicle
            dist_lambda = model.lambda_function(lambda i: model.at(dist_matrix, route[i - 1], route[i]))
            depot_id = vehicles_depots[k]
            routes_lens[k] = model.sum(model.range(1, c), dist_lambda) + model.iif(c > 0, dist_from_depots[depot_id][route[0]] + dist_to_depots[depot_id][route[c - 1]], 0)

        # Total number of vehicles
        vehicles_used_cnt = model.sum(vehicles_used)
        # model.constraint(vehicles_used_cnt == vehicles_cnt)

        # OBJECTIVES
        # Total distance traveled
        max_distance = model.max(routes_lens)

        # Objective: minimize the distance traveled
        model.minimize(max_distance)
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
            {"name": "max_distance", "value": sol.get_value(max_distance), "bound": sol.get_objective_bound(0), "gap": sol.get_objective_gap(0)}
            ]
        result["routes"] = []
        for k in range(vehicles_cnt):
            if vehicles_used[k].value:
                route = [station for station in routes[k].value]
                leaving_load = [load for load in loads[k].value]
                result["routes"].append({"route": route, "leaving_load": leaving_load})
        
        result_string = json.dumps(result, indent=4)

        with open(solution_path, "w") as outfile:
            outfile.write(result_string)
            print("Solution exported to", solution_path)






if __name__ == "__main__":
    # DEFAULT PARAMETERS
    instance_path = "./data/instances_v2/n10_v4_d2.json"
    solution_path = "./results/v2-1_minmax/demo.json"
    time_limit = 5

    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i':
            instance_path = sys.argv[i+1]
        elif sys.argv[i] == '-o':
            solution_path = sys.argv[i+1]
        elif sys.argv[i] == '-t':
            time_limit = int(sys.argv[i+1])

    rebalance_v2_1_minmax(instance_path, solution_path, time_limit)