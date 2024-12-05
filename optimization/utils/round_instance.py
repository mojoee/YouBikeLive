#!/usr/bin/env python3

import json

instance_path = "data/instances/demo.json"

data = {}
with open(instance_path, 'r') as file:
    data = json.load(file)

    data["depot"]["dists_from_depot"] = [int(d) for d in data["depot"]["dists_from_depot"]]
    data["depot"]["dists_to_depot"] = [int(d) for d in data["depot"]["dists_to_depot"]]

    for i in range(len(data["distances"])):
        data["distances"][i] = [int(d) for d in data["distances"][i]]


# output_path = instance_path.replace(".json", "_round.json")
output_path = instance_path
with open(output_path, "w") as outfile:
    json.dump(data, outfile, indent=4)
    print("Exported instance", output_path)
