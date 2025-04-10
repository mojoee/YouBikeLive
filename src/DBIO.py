import sqlite3
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import urllib.request
import json
import os

# Weather stations with their coordinates
weather_stations_data = [
    ("Anpu", 121.5297306, 25.18258611),
    ("Taipei", 121.514853, 25.037658),
    ("Yangmingshan", 121.5445472, 25.16207778),
    ("NTU", 121.539416, 25.014278),
    ("PCCU", 121.53987, 25.13605),
    ("Science Education Center", 121.516506, 25.096356),
    ("Shezi", 121.469681, 25.109508),
    ("Tianmu", 121.537169, 25.117494),
    ("Neihu", 121.57545, 25.079422),
    ("Datunshan", 121.522408, 25.175675),
    ("Xinyi", 121.564597, 25.037822),
    ("Wenshan", 121.575728, 25.00235),
    ("Pingdeng", 121.577086, 25.129142),
    ("Songshan", 121.550428, 25.048711),
    ("Shipai", 121.513139, 25.115597),
    ("Freeway No. 3 - CCTV – S016K", 121.6158, 25.03306),
    ("Freeway No. 3 - CCTV – A005K", 121.5975, 25.00194),
    ("Da'an Forest Park", 121.53628, 25.02955),
    ("Agriculture Guandu Station", 121.492, 25.11575),
]


class YouBikeDataManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def fetch_stations(self):
        query = """
        SELECT 
            youbike_stations.sno, 
            youbike_stations.sna,
            youbike_stations.snaen, 
            youbike_stations.sareaen, 
            youbike_stations.ar,
            youbike_stations.latitude, 
            youbike_stations.longitude, 
            youbike_stations.capacity
        FROM youbike_stations
        GROUP BY youbike_stations.sno
        ORDER BY youbike_stations.sno;
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def fetch_all_stations(self):
        # Query to fetch bike stations
        bike_stations_query = """
        SELECT sno AS station_id, sna AS name, latitude, longitude
        FROM youbike_stations;
        """
        bike_stations = pd.read_sql_query(bike_stations_query, self.conn)

        # Query to fetch weather stations
        weather_stations_query = """
        SELECT name AS station_name, latitude, longitude
        FROM weather_stations;
        """
        weather_stations = pd.read_sql_query(weather_stations_query, self.conn)

        return bike_stations, weather_stations


    def load_and_preprocess_station(self, station_id: str):
        query = f"""
        SELECT available_rent_bikes, mday, available_return_bikes
        FROM youbike_status
        WHERE sno = '{station_id}'
        ORDER BY mday ASC;
        """
        df = pd.read_sql_query(query, self.conn)

        # Processing logic remains the same
        df['mday'] = pd.to_datetime(df['mday'])
        df = df.set_index('mday')
        df = df.resample('1h').mean().ffill()

        stations_df = self.fetch_stations()
        capacity = stations_df.loc[stations_df['sno'] == station_id, 'capacity'].values[0]
        df["available_return_bikes"] = df["available_return_bikes"].astype(int)
        df['capacity'] = capacity
        df['available_rent_bikes'] = df['capacity']-df['available_return_bikes']

        # Compute demand (same logic as before)
        df['demand'] = self._compute_demand(df, capacity)
        return df

    def _compute_demand(self, df, capacity):
        demands = []
        prev_bikes = None
        capacity = max(df['capacity'])
        for curr_bikes in df['available_rent_bikes']:
            if prev_bikes is None:
                demand = 0
            # we check if the station is full or empty
            # if the station is full, we assume that the 
            # demand is similar to the previous demand
            elif curr_bikes == capacity or curr_bikes == 0:
                demand = demands[-1] 
            else:
                demand = prev_bikes - curr_bikes
            demands.append(demand)
            prev_bikes = curr_bikes
        return demands

    def get_station_available_bikes_at_time(self, sno, time):
        self.connect()
        query = f"""
        SELECT *
        FROM youbike_status
        WHERE sno = '{sno}' AND mday <= '{time}'
        ORDER BY mday DESC
        LIMIT 1;
        """
        df = pd.read_sql_query(query, self.conn)
        if df.empty:
            return 0
        else:
            return int(df['available_rent_bikes'].values[0])

    def load_data(self):
        load_dotenv()
        GMAPS_API_KEY = os.environ['GMAPS_API_KEY']
        url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        return data

    # Create and populate the weather_stations table
    def create_and_populate_weather_stations(self):
        cursor = self.conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        );
        """
        )

        # Insert data into the table
        cursor.executemany(
            "INSERT INTO weather_stations (name, longitude, latitude) VALUES (?, ?, ?);",
            weather_stations_data
        )

        self.conn.commit()
        self.conn.close()
        print("Weather stations table created and populated.")


if __name__ == "__main__":
    db_path = 'youbike_data.db'
    data_manager = YouBikeDataManager(db_path)
    data_manager.create_and_populate_weather_stations()
    data_manager.close()
    print("Weather stations table created and populated.")