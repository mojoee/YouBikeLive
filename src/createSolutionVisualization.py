import json
import folium
import pandas as pd

# Load the instance (stations and their details)
def load_instance(instance_path):
    with open(instance_path, 'r') as f:
        instance = json.load(f)
    return instance

# Load the TSP solution (order of visits)
def load_solution(solution_path):
    with open(solution_path, 'r') as f:
        solution = json.load(f)
    return solution['routes'][0]['route']  # Assuming the solution file contains a key 'tsp_solution'

# Visualize the path on a map
def visualize_tsp_path(instance, tsp_solution, map_output="./results/visualizations/tsp_map.html"):
    # Convert stations to a DataFrame for easy handling
    stations = pd.DataFrame(instance['stations'])

    # Initialize a folium map centered on the first station
    first_station = stations.iloc[tsp_solution[0]]
    map_center = first_station['coords'][0], first_station['coords'][1]
    mymap = folium.Map(location=map_center, zoom_start=13)

    # Add stations as markers
    for _, row in stations.iterrows():
        folium.Marker(
            location=row['coords'],  # Coordinates of the station
            popup=f"Station ID: {row['id']}, Capacity: {row['capacity']}",
            tooltip=f"Station ID: {row['id']}"
        ).add_to(mymap)

    # Add the TSP path
    path_coordinates = [stations.iloc[i]['coords'] for i in tsp_solution]
    folium.PolyLine(
        path_coordinates, color="blue", weight=2.5, opacity=1
    ).add_to(mymap)

    # Save the map
    mymap.save(map_output)
    print(f"Map saved as '{map_output}'")

# Example usage
instance_path = "./data/instances/instance_test_12:30.json"  # Path to the generated instance file
solution_path = "./results/instance_test_12_30/v5_20min.json"  # Path to the TSP solution file
solution = solution_path.split('/')[-1].split('.')[0]
instance = instance_path.split('/')[-1].split('.')[0]
name = solution + instance
save_path = f"./results/visualizations/{name}_tsp_map.html"

# Load instance and solution
instance = load_instance(instance_path)
tsp_solution = load_solution(solution_path)

# Visualize the TSP solution
visualize_tsp_path(instance, tsp_solution, save_path)
