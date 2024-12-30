import sqlite3
import pandas as pd


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