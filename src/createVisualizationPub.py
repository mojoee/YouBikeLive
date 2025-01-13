import folium
import pandas as pd
from folium.plugins import MarkerCluster
from DBIO import YouBikeDataManager

# Database path
DB_PATH = "youbike_data.db"  # Update with the actual database path

# Initialize the data manager
data_manager = YouBikeDataManager(DB_PATH)
# if data_manager.conn is None:
#     raise ConnectionError("Failed to connect to the database. Please check the database path.")

# Visualize the stations on a map
def visualize_stations(map_output, manager=data_manager):
    bike_stations, weather_stations = manager.fetch_all_stations()

    # Initialize the map centered on the average location of all stations
    avg_lat = bike_stations["latitude"].mean()
    avg_lon = bike_stations["longitude"].mean()
    station_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    # Add bike stations to the map with a blue marker cluster
    bike_cluster = MarkerCluster(name="Bike Stations").add_to(station_map)
    for _, row in bike_stations.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"Bike Station: {row['name']} (ID: {row['station_id']})",
            icon=folium.Icon(color="blue", icon="bicycle"),
        ).add_to(bike_cluster)

    # Add weather stations to the map with red markers
    for _, row in weather_stations.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"Weather Station: {row['station_name']}",
            icon=folium.Icon(color="red", icon="cloud"),
        ).add_to(station_map)

    # Add layer control for toggling markers
    folium.LayerControl().add_to(station_map)

    # Save the map to an HTML file
    station_map.save(map_output)
    print(f"Map saved as '{map_output}'")


if __name__ == "__main__":
    # Path to save the map
    save_path = "./visualizations/stations_map.html"

    try:
        # Generate and save the map
        visualize_stations(save_path)
    finally:
        # Close the database connection
        data_manager.close()
