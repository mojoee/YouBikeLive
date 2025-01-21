#!/bin/bash

INSTANCE_DIR="./data/instances_v4/naive_21/"
TIMEOUT=5

# Generate unit solutions for proportional instances
OUTPUT="./results/v4_unit/naive_21/"
SCRIPT="./optimization/models/rebalance_unit.py"
INSTANCES="proportional"

for INSTANCE in "$INSTANCE_DIR"*.json; do
    if [[ "$INSTANCE" == *$INSTANCES* ]]; then
        echo "Solving instance: $INSTANCE"
        python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4
    fi
done

# Generate ws solutions for proportional instances
OUTPUT="./results/v4_cbws/naive_21/"
SCRIPT="./optimization/models/rebalance_v4_cbws.py"
INSTANCES="proportional"

for INSTANCE in "$INSTANCE_DIR"*.json; do
    if [[ "$INSTANCE" == *$INSTANCES* ]]; then
        echo "Solving instance: $INSTANCE"
        python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT
    fi
done

# Generate cb solutions for all instances
OUTPUT="./results/v4_cb/naive_21/"
SCRIPT="./optimization/models/rebalance_unit.py"

for INSTANCE in "$INSTANCE_DIR"*.json; do
    echo "Solving instance: $INSTANCE"
    python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4_cb
done

# Generate v5 solutions for all instances
OUTPUT="./results/v5/naive_21/"
SCRIPT="./optimization/models/rebalance_v5.py"

for INSTANCE in "$INSTANCE_DIR"*.json; do
    echo "Solving instance: $INSTANCE"
    python3 $SCRIPT -i $INSTANCE -o $OUTPUT -t $TIMEOUT
done




# INSTANCE=./data/instances_v4/v12-24-24_b8h_uniform_goal.json
# TIMEOUT=3600

# OUTPUT=./results/v4/
# python3 ./optimization/models/rebalance_v4.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT

# OUTPUT=./results/v4_unit/
# python3 ./optimization/models/rebalance_unit.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4

# OUTPUT=./results/v4_cb/
# python3 ./optimization/models/rebalance_unit.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4_cb

# OUTPUT=./results/v4_cbws/
# python3 ./optimization/models/rebalance_v4_cbws.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT

# OUTPUT=./results/v5_1/
# python3 ./optimization/models/rebalance_v5_1.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT