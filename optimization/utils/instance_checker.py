#!/usr/bin/env python3

import sys
import json
from geopy.distance import geodesic
from pytest import approx


for i in range(len(sys.argv)):
    if sys.argv[i] == '-i':
        instance_path = sys.argv[i+1]


# LOAD
with open(instance_path, 'r') as file:
    instance_data = json.load(file)

    stations_cnt = len(instance_data["stations"])
    
    c1 = True
    for i in range(stations_cnt):
        print(i)
        for j in range(stations_cnt):
            s1 = instance_data["stations"][i]["coords"]
            s2 = instance_data["stations"][j]["coords"]
            dist1 = geodesic(s1, s2).m
            dist2 = instance_data["distances"][i][j]
            c1 = c1 and (dist1 == approx(dist2))

    c2 = True
    c3 = True
    c4 = True
    depot = instance_data["depot"]["coords"]
    for i in range(stations_cnt):
        s1 = instance_data["stations"][i]["coords"]
        dist1 = geodesic(depot, s1).m
        dist2 = geodesic(s1, depot).m
        c2 = c2 and (dist1 == instance_data["depot"]["dists_from_depot"][i])
        c3 = c3 and (dist2 == instance_data["depot"]["dists_to_depot"][i])        
        c4 = instance_data["stations"][i]["id"] == i

    print("Distance matrix: ", c1)
    print("Dists from depot: ", c2)
    print("Dists to depot:", c3)
    print("Ids match:", c4)