import requests
import sqlite3
from datetime import datetime
import schedule
import time
import logging

# JSON endpoint
URL = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'

# Logging configuration
logging.basicConfig(level=logging.INFO, filename='data_collector.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the SQLite database (or create it)SELECT 
conn = sqlite3.connect('youbike_data.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS youbike_stations (
        sno TEXT PRIMARY KEY,
        sna TEXT,
        sarea TEXT,
        ar TEXT,
        sareaen TEXT,
        snaen TEXT,
        aren TEXT,
        latitude REAL,
        longitude REAL,
        capacity INTEGER
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS youbike_status (
        sno TEXT,
        mday TEXT,
        available_rent_bikes INTEGER,
        available_return_bikes INTEGER,
        PRIMARY KEY (sno, mday),
        FOREIGN KEY (sno) REFERENCES youbike_stations(sno)
    )
''')
conn.commit()

def fetch_and_store():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()

        for record in data:
            # Extract station information
            station_info = (
                record["sno"], record["sna"], record["sarea"], record["ar"],
                record["sareaen"], record["snaen"], record["aren"],
                float(record["latitude"]), float(record["longitude"]), int(record["total"])
            )

            # Insert station information
            cursor.execute('''
                INSERT OR IGNORE INTO youbike_stations (
                    sno, sna, sarea, ar, sareaen, snaen, aren, latitude, longitude, capacity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', station_info)

            # Extract status information
            status_info = (
                record["sno"], record["mday"],
                int(record.get("available_rent_bikes", 0)),
                int(record.get("available_return_bikes", 0))
            )

            # Insert status information
            cursor.execute('''
                INSERT OR IGNORE INTO youbike_status (
                    sno, mday, available_rent_bikes, available_return_bikes
                ) VALUES (?, ?, ?, ?)
            ''', status_info)

        conn.commit()
        logging.info("Data stored successfully.")

    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Retry mechanism
while True:
    try:
        schedule.every(10).minutes.do(fetch_and_store)

        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        logging.error(f"Script crashed with error: {e}. Restarting...")
        time.sleep(5)
