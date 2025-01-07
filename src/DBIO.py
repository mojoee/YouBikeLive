import urllib, json
import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
import numpy as np

db_path = "./youbike_data.db"


def load_data():
    load_dotenv()
    GMAPS_API_KEY=os.environ['GMAPS_API_KEY']
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data


def fetch_stations(db_path):
    """
    Fetch station data from the database.

    Args:
        start_time (str): Start time in '%H:%M' format.
        end_time (str): End time in '%H:%M' format.

    Returns:
        pd.DataFrame: Aggregated station data.
    """
    conn = sqlite3.connect(db_path)

    query = f"""
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
    GROUP BY youbike_stations.sno, youbike_stations.sna, youbike_stations.snaen, youbike_stations.sareaen, youbike_stations.latitude, youbike_stations.longitude, youbike_stations.capacity
    ORDER BY youbike_stations.sno;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    df.rename(columns={"s_init": "s_init"}, inplace=True)
    return df


def load_and_preprocess_station(station_id):
    '''
    loads data from a specific station and preprocesses it
    '''
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT *
    FROM youbike_status
    WHERE sno = '{station_id}'
    ORDER BY mday ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Ensure `mday` is in datetime format for resampling
    df['mday'] = pd.to_datetime(df['mday'])
    df = df.set_index('mday')

    # Drop non-numeric columns
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    df = df.drop(columns=non_numeric_cols, errors='ignore')

    # Resample and fill missing values
    df = df.resample('1h').mean().round().ffill()

    # Ensure `capacity` is present
    if 'capacity' not in df.columns:
        df_stations = fetch_stations(db_path)
        cap = df_stations.loc[df_stations['sno'] == station_id, 'capacity']
        if len(cap) > 0:
            capacity = cap.iloc[0]
        else:
            capacity = df['available_rent_bikes'].max()  # Fallback guess
        df['capacity'] = capacity
    else:
        capacity = df['capacity'].mean()

    # Compute demand
    demands = []
    prev_bikes = None
    prev_demand = 0
    for t in df.index:
        curr_bikes = df.at[t, 'available_rent_bikes']
        if prev_bikes is None:
            demand = 0
        else:
            raw_demand = prev_bikes - curr_bikes
            if curr_bikes == 0:
                if prev_bikes > 0:
                    demand = prev_bikes
                else:
                    demand = prev_demand if prev_demand > 0 else 1
            elif curr_bikes == capacity:
                if prev_bikes < capacity:
                    demand = prev_bikes - capacity
                else:
                    demand = prev_demand if prev_demand < 0 else -1
            else:
                demand = raw_demand

        demands.append(demand)
        prev_bikes = curr_bikes
        prev_demand = demand

    df['demand'] = demands
    return df


def get_station_available_bikes_at_time(sno, time):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT *
    FROM youbike_status
    WHERE sno = '{sno}' AND mday <= '{time}'
    ORDER BY mday DESC
    LIMIT 1;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        return 0
    else:
        return int(df['available_rent_bikes'].values[0])
