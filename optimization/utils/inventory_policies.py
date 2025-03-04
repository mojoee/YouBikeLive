#!/usr/bin/env python3

import numpy as np

def get_inventories(demands, s_init, s_cap):
    n = len(demands)
    inventories = np.zeros(n + 1, dtype=int)
    inventories[0] = s_init
    for t in range(1, n + 1):
        inventories[t] = min(max(0, inventories[t-1] + demands[t-1]), s_cap)
    return inventories

def get_P_max(demands, inventories, s_cap):
    n = len(demands)
    over = [int(max(inventories[t] + demands[t] - s_cap, 0)) for t in range(n)]
    P_over = max(over)
    # print("over:", over)
    # print("P_over:", P_over)
    short = [abs(int(min(inventories[t] + demands[t], 0))) for t in range(n)]
    P_short = max(short)
    # print("short:", short)
    # print("P_short:", P_short)
    P_max = max(P_over, P_short)
    return P_max



np.random.seed(0)
s_init = 10
s_cap = 30
n = 6
demands = np.random.randint(-40, 40, size=n)
inventories = get_inventories(demands, s_init, s_cap)
P_max = get_P_max(demands, inventories, s_cap)

print("s_init:", s_init)
print("s_cap:", s_cap)
print("n:", n)
print("demands:", demands)
print("inventories:", inventories)
print("P_max:", P_max)