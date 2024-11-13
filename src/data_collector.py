import requests
import sqlite3
from datetime import datetime
import schedule
import time


# JSON endpoint
URL = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'


# Connect to the SQLite database (or create it)
conn = sqlite3.connect('youbike_data.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS youbike_data (
        sno TEXT,
        sna TEXT,
        sarea TEXT,
        mday TEXT,
        ar TEXT,
        sareaen TEXT,
        snaen TEXT,
        aren TEXT,
        act INTEGER,
        srcUpdateTime TEXT,
        updateTime TEXT,
        infoTime TEXT,
        infoDate TEXT,
        total INTEGER,
        available_rent_bikes INTEGER,
        latitude REAL,
        longitude REAL,
        available_return_bikes INTEGER,
        PRIMARY KEY (sno, mday) -- Prevent duplicate entries based on unique station and time
    )
''')
conn.commit()

# Function to fetch and store JSON data
def fetch_and_store():
    try:
        response = requests.get(URL)  # Replace with the actual endpoint
        response.raise_for_status()
        data = response.json()

        for record in data:
            # Insert each record into the database
            cursor.execute('''
                INSERT OR IGNORE INTO youbike_data (
                    sno, sna, sarea, mday, ar, sareaen, snaen, aren, act,
                    srcUpdateTime, updateTime, infoTime, infoDate, total,
                    available_rent_bikes, latitude, longitude, available_return_bikes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record["sno"], record["sna"], record["sarea"], record["mday"], record["ar"],
                record["sareaen"], record["snaen"], record["aren"], int(record["act"]),
                record["srcUpdateTime"], record["updateTime"], record["infoTime"], record["infoDate"],
                int(record["total"]), int(record["available_rent_bikes"]),
                float(record["latitude"]), float(record["longitude"]), int(record["available_return_bikes"])
            ))

        conn.commit()
        print("Data stored successfully.")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

# Schedule the function to run every minute
schedule.every(1).minutes.do(fetch_and_store)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
