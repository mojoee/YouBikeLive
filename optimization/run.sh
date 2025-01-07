INSTANCE=./data/instances_v4/v12-24-24_b8h_uniform_goal.json
TIMEOUT=30

OUTPUT=./results/v4/
python3 ./optimization/models/rebalance_v4.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT

OUTPUT=./results/v4_unit/
python3 ./optimization/models/rebalance_unit.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4

OUTPUT=./results/v4_cb/
python3 ./optimization/models/rebalance_unit.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT -f v4_cb

OUTPUT=./results/v4_cbws/
python3 ./optimization/models/rebalance_v4_cbws.py -i $INSTANCE -o $OUTPUT -t $TIMEOUT