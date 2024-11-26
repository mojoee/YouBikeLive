import json
import folium
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as colors

# Load the instance (stations and their details)
def load_instance(instance_path):
    with open(instance_path, 'r') as f:
        instance = json.load(f)
    return instance

# Load the TSP solution (routes for multiple trucks)
def load_solution(solution_path):
    with open(solution_path, 'r') as f:
        solution = json.load(f)
    return solution['routes']  # Assuming the solution file contains a key 'routes'

# Visualize the paths on a map
def visualize_tsp_paths(instance, tsp_routes, map_output="./results/visualizations/tsp_map.html"):
    # Convert stations to a DataFrame for easy handling
    stations = pd.DataFrame(instance['stations'])

    # Initialize a folium map centered on the first station
    first_route = tsp_routes[0]['route']
    first_station = stations.iloc[first_route[0]]
    map_center = first_station['coords'][0], first_station['coords'][1]
    mymap = folium.Map(location=map_center, zoom_start=13)

    # Add a FeatureGroup for station markers
    marker_group = folium.FeatureGroup(name="Stations")

    # Add smaller markers to the FeatureGroup
    for _, row in stations.iterrows():
        folium.CircleMarker(
            location=row['coords'],  # Coordinates of the station
            radius=5,                # Adjust radius for smaller markers
            color="blue",            # Border color of the circle
            fill=True,               # Fill the circle with color
            fill_color="blue",       # Fill color of the circle
            fill_opacity=0.7,        # Adjust transparency
            tooltip=f"Station ID: {row['id']}"  # Tooltip on hover
        ).add_to(marker_group)

    # Add the FeatureGroup to the map
    marker_group.add_to(mymap)

    # Generate a color palette for the routes
    num_routes = len(tsp_routes)
    colormap = cm.get_cmap('tab10', num_routes)  # Use a discrete colormap
    route_colors = [colors.rgb2hex(colormap(i)[:3]) for i in range(num_routes)]

    # Add the TSP paths with unique colors
    for idx, route in enumerate(tsp_routes):
        path_coordinates = [stations.iloc[i]['coords'] for i in route['route']]
        folium.PolyLine(
            path_coordinates, color=route_colors[idx], weight=2.5, opacity=1,
            tooltip=f"Route {idx + 1}"
        ).add_to(mymap)

    # Add LayerControl to enable toggling
    folium.LayerControl().add_to(mymap)

    # Save the map
    mymap.save(map_output)
    print(f"Map saved as '{map_output}'")

# Example usage
instance_path = "./data/instances/instance_test_12:30.json"  # Path to the generated instance file
solution_path = "./results/instance_test_12_30/v5_c100_20min.json"  # Path to the TSP solution file
solution = solution_path.split('/')[-1].split('.')[0]
instance = instance_path.split('/')[-1].split('.')[0]
name = solution + instance
save_path = f"./results/visualizations/{name}_tsp_map.html"

# Load instance and solution
instance = load_instance(instance_path)
tsp_routes = load_solution(solution_path)

# Visualize the TSP solution
visualize_tsp_paths(instance, tsp_routes, save_path)
