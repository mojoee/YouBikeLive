import sqlite3
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json
from config import cfg 

# Connect to the SQLite database
conn = sqlite3.connect('youbike_data.db')

# Query the latest data from the database
# Execute the query
def fetch_stations(time_of_interest):

    query = f"""
    WITH RankedStations AS (
        SELECT 
            sno, 
            snaen, 
            latitude, 
            longitude, 
            total AS capacity, 
            available_rent_bikes AS s_init, 
            mday,
            ROW_NUMBER() OVER (PARTITION BY sno ORDER BY mday ASC) AS rank
        FROM youbike_data
        WHERE strftime('%H:%M', mday) >= '{time_of_interest}'
    )
    SELECT 
        sno, 
        snaen, 
        latitude, 
        longitude, 
        capacity, 
        s_init, 
        mday
    FROM RankedStations
    WHERE rank = 1
    """
    df = pd.read_sql_query(query, conn)

    # Close the connection
    conn.close()
    return df


# Compute the total number of bikes and total capacity
time = cfg.instance_time
df = fetch_stations(time)
total_bikes = df['s_init'].sum()
total_capacity = df['capacity'].sum()

# Proportional bike allocation
proportions = (df['capacity'] / total_capacity) * total_bikes
df['s_goal_int'] = proportions.astype(int)  # Initial allocation as integers
df['fraction'] = proportions - df['s_goal_int']  # Fractional part for fine-tuning

# Adjust to ensure the sum of s_goal equals total_bikes
remaining_bikes = total_bikes - df['s_goal_int'].sum()

# Distribute the remaining bikes to stations with the largest fractional part
df = df.sort_values(by='fraction', ascending=False)
df.iloc[:remaining_bikes, df.columns.get_loc('s_goal_int')] += 1

# Finalize s_goal
df['s_goal'] = df['s_goal_int']
df = df.drop(columns=['s_goal_int', 'fraction'])

# Depot configuration
depot = {
    "capacity": 0,
    "s_init": 0,
    "s_goal": 0,
    "coords": [25.02000, 121.53300]  # Example depot coordinates
}

df.reset_index(inplace=True)
# Compute distances between stations and to/from the depot
station_coords = df[['latitude', 'longitude']].values
depot_coords = np.array(depot['coords'])

# Calculate distances from depot to stations and vice versa
dists_from_depot = [geodesic(depot_coords, station).meters for station in station_coords]
dists_to_depot = dists_from_depot[:]  # Symmetric distance

# Calculate pairwise distances between stations
num_stations = len(station_coords)
distances = np.zeros((num_stations, num_stations))

for i in range(num_stations):
    for j in range(num_stations):
        distances[i][j] = geodesic(station_coords[i], station_coords[j]).meters

# Create stations list
stations = []
for idx, row in df.iterrows():
    station = {
        "id": idx,
        "true_id": row['sno'],
        "station name": row['snaen'],
        "capacity": row['capacity'],
        "s_init": row['s_init'],
        "s_goal": row['s_goal'],
        "coords": [row['latitude'], row['longitude']]
    }
    stations.append(station)

# Assemble the final JSON object
instance = {
    "depot": {
        "capacity": depot['capacity'],
        "s_init": depot['s_init'],
        "s_goal": depot['s_goal'],
        "coords": depot['coords'],
        "dists_from_depot": dists_from_depot,
        "dists_to_depot": dists_to_depot
    },
    "stations": stations,
    "distances": distances.tolist(),  # Convert NumPy array to list
    "vehicles": {
        "count": 2,  # Example vehicle count
        "capacity": 20  # Example vehicle capacity
    }
}

# Print or save the result
# name is 
name = f"test_{time}"
output_file = f"./data/instances/instance_{name}.json"
with open(output_file, "w") as f:
    json.dump(instance, f, indent=4)
print(f"Instance saved to {output_file}")
