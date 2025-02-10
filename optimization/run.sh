#!/bin/bash

# INSTANCE_DIR="./data/instances_v4/naive_21/"

# # Generate unit solutions for proportional instances
# OUTPUT="./results/v4_unit/naive_21/"
# SCRIPT="./optimization/models/rebalance_unit.py"
# INSTANCES="proportional"
# TIMEOUT=3600

# for INSTANCE in "$INSTANCE_DIR"*.json; do
#     if [[ "$INSTANCE" == *$INSTANCES* ]]; then
#         echo "Solving instance: $INSTANCE"
#         python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4 -r
#     fi
# done

# # Generate cbws solutions for proportional instances 
# OUTPUT="./results/v4_cbws/naive_21/"
# SCRIPT="./optimization/models/rebalance_v4_cbws.py"
# INSTANCES="proportional"
# TIMEOUT=3600

# for INSTANCE in "$INSTANCE_DIR"*.json; do
#     if [[ "$INSTANCE" == *$INSTANCES* ]]; then
#         echo "Solving instance: $INSTANCE"
#         python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT -r
#     fi
# done

# # Generate cb solutions for all instances
# OUTPUT="./results/v4_cb/naive_21/"
# SCRIPT="./optimization/models/rebalance_unit.py"
# TIMEOUT=3600

# for INSTANCE in "$INSTANCE_DIR"*.json; do
#     echo "Solving instance: $INSTANCE"
#     python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4_cb -r
# done

# Generate v5 solutions for all instances
# OUTPUT="./results/v5/naive_21/"
# SCRIPT="./optimization/models/rebalance_v5.py"
# TIMEOUT=3600

# for INSTANCE in "$INSTANCE_DIR"*.json; do
#     echo "Solving instance: $INSTANCE"
#     python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT
# done







INSTANCE_DIR="./data/instances_v4/rnd_large_2/"

# Generate cb solutions for all instances
OUTPUT="./results/v4_cb/rnd_large_2/"
SCRIPT="./optimization/models/rebalance_unit.py"
TIMEOUT=3600

for INSTANCE in "$INSTANCE_DIR"*.json; do
    echo "Solving instance: $INSTANCE"
    python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4_cb -r
done

# Generate v5 solutions for all instances
OUTPUT="./results/v5/rnd_large/"
SCRIPT="./optimization/models/rebalance_v5.py"
TIMEOUT=3600

for INSTANCE in "$INSTANCE_DIR"*.json; do
    echo "Solving instance: $INSTANCE"
    python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT
done