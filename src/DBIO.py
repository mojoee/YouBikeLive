import sqlite3
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import urllib.request
import json
import os


class YouBikeDataManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def fetch_stations(self):
        self.connect()
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

    def load_and_preprocess_station(self, station_id):
        self.connect()
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
        for curr_bikes in df['available_rent_bikes']:
            if prev_bikes is None:
                demand = 0
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
