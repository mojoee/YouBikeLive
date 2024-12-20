import requests
import sqlite3
import numpy as np
import pandas as pd
from tqdm import tqdm

# OSRM API base URL
OSRM_URL = "http://localhost:5000/route/v1/driving"

# Database connection
DB_PATH = "youbike_data.db"


def get_coordinates_from_db():
    """
    Fetch station coordinates from the SQLite database.

    Returns:
        list: List of coordinates in (longitude, latitude) format.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sno, snaen, longitude, latitude FROM youbike_stations ORDER BY youbike_stations.sno;")
        coordinates = cursor.fetchall()  # Returns a list of tuples [(lon, lat), ...]

    unique_coordinates = list(set(coordinates))
    return unique_coordinates


def make_osrm_request(coordinates):
    """
    Make an OSRM route API call using the provided coordinates.

    Args:
        coordinates (list): List of (longitude, latitude) tuples.

    Returns:
        dict: The response JSON from the OSRM API.
    """
    # Format the coordinates for the OSRM API
    coord_string = ";".join([f"{lon},{lat}" for _, _, lon, lat in coordinates])

    # Construct the full URL
    url = f"{OSRM_URL}/{coord_string}?steps=false"

    try:
        # Make the API call
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error making OSRM request: {e}")
        return None


if __name__ == "__main__":
    # Step 1: Fetch coordinates from the database
    coordinates = get_coordinates_from_db()
    if len(coordinates) < 2:
        print("Not enough coordinates to calculate a route. At least two are required.")
        exit()

    # Step 2: Select start and end points for the route
    start_coord = coordinates[0]  # First coordinate (longitude, latitude)
    end_coord = coordinates[1]    # Second coordinate (longitude, latitude)

    # Step 3: Make the OSRM API call
    response = make_osrm_request([start_coord, end_coord])

    # Step 4: Print the result
    if response:
        print("OSRM Response:")
        print(response)

    distance_matrix = np.zeros((len(coordinates), len(coordinates)))
    for i, coord_1 in tqdm(enumerate(coordinates)):
        for j, coord_2 in enumerate(coordinates):
            response = make_osrm_request([coord_1, coord_2])
            distance_matrix[i][j] = response['routes'][0]['legs'][0]['duration']

    df = pd.DataFrame(distance_matrix, columns=[x for x, _, _, _ in coordinates])
    print(df.head())
    df.to_csv("distance_matrix.csv", index=False)
