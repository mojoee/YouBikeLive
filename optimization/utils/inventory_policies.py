#!/usr/bin/env python3

import numpy as np

def get_inventories(demands, s_init, s_cap):
    n = len(demands)
    inventories = np.zeros(n + 1, dtype=int)
    inventories[0] = s_init
    for t in range(1, n + 1):
        inventories[t] = min(max(0, inventories[t-1] + demands[t-1]), s_cap)
    return inventories


# Get peak unmet demand, positive or negative
def get_P_max(demands, inventories, s_cap):
    n = len(demands)
    over = [int(max(inventories[t] + demands[t] - s_cap, 0)) for t in range(n)]
    P_over = max(over)
    # print("demands:", demands)
    # print("inventories:", inventories)
    # print("over:", over)
    # print("P_over:", P_over)
    short = [abs(int(min(inventories[t] + demands[t], 0))) for t in range(n)]
    P_short = max(short)
    # print("short:", short)
    # print("P_short:", P_short)
    P_max = max(P_over, P_short)
    return P_max


# Get total unmet demand, positive and negative
def get_Q_total(demands, inventories, s_cap):
    n = len(demands)
    over = [int(max(inventories[t] + demands[t] - s_cap, 0)) for t in range(n)]
    Q_over = sum(over)
    # print("over:", over)
    # print("Q_over:", Q_over)
    short = [abs(int(min(inventories[t] + demands[t], 0))) for t in range(n)]
    Q_short = sum(short)
    # print("short:", short)
    # print("Q_short:", Q_short)
    Q_total = Q_over + Q_short
    return Q_total


# Returns s_init, so that P_max in minimal
def min_P_max_policy(demands, s_cap):
    min_P_max = float('inf')
    best_s_init_cands = []
    for s_init_cand in range(s_cap + 1):
        inventories = get_inventories(demands, s_init_cand, s_cap)
        P_max = get_P_max(demands, inventories, s_cap)
        # print("s_init_cand:", s_init_cand, "P_max:", P_max)
        if P_max < min_P_max:
            min_P_max = P_max
            best_s_init_cands = [s_init_cand]
        elif P_max == min_P_max:
            best_s_init_cands.append(s_init_cand)
    # print(best_s_init_cands)
    s_init = int(np.median(best_s_init_cands))
    # print(s_init)
    return s_init


# Returns s_init, so that Q_total in minimal
def min_Q_total_policy(demands, s_cap):
    min_Q_total = float('inf')
    best_s_init_cands = []
    for s_init_cand in range(s_cap + 1):
        inventories = get_inventories(demands, s_init_cand, s_cap)
        Q_total = get_Q_total(demands, inventories, s_cap)
        # print("s_init_cand:", s_init_cand, "Q_total:", Q_total)
        if Q_total < min_Q_total:
            min_Q_total = Q_total
            best_s_init_cands = [s_init_cand]
        elif Q_total == min_Q_total:
            best_s_init_cands.append(s_init_cand)
    # print(best_s_init_cands)
    s_init = int(np.median(best_s_init_cands))
    # print(s_init)
    return s_init


if __name__ == "__main__":
    np.random.seed(0)
    n = 12
    demands = np.random.randint(-15, 15, size=n)
    s_cap = 20

    # s_init = 10
    # inventories = get_inventories(demands, s_init, s_cap)
    # P_max = get_P_max(demands, inventories, s_cap)
    # Q_total = get_Q_total(demands, inventories, s_cap)

    s_init_1 = min_P_max_policy(demands, s_cap)
    inventories_1 = get_inventories(demands, s_init_1, s_cap)

    s_init_2 = min_Q_total_policy(demands, s_cap)
    inventories_2 = get_inventories(demands, s_init_2, s_cap)  

    print("demands: ", demands)
    print("s_cap: ", s_cap)
    print("s_init_1: ", s_init_1)
    print("inventories_1: ", inventories_1)
    print("s_init_2: ", s_init_2)
    print("inventories_2: ", inventories_2)
