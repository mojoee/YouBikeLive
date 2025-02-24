import requests
import sqlite3
from datetime import datetime
import schedule
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")  # If running in a virtual environment

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(60)  # Increase timeout to 60 seconds

# Logging configuration
logging.basicConfig(level=logging.INFO, filename='data_collector.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Data collector started.")

# Database setup
db_path = 'youbike_data.db'
conn = sqlite3.connect(db_path)
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
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        station_name TEXT,
        observe_time TEXT,
        temperature REAL,
        weather TEXT,
        wind_direction TEXT,
        wind_speed REAL,
        gust REAL,
        visibility TEXT,
        humidity INTEGER,
        pressure REAL,
        rainfall REAL,
        sunshine TEXT,
        PRIMARY KEY (station_name, observe_time)
    )
''')
conn.commit()

# YouBike data fetch function
URL = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'

def fetch_youbike_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()

        for record in data:
            station_info = (
                record["sno"], record["sna"], record["sarea"], record["ar"],
                record["sareaen"], record["snaen"], record["aren"],
                float(record["latitude"]), float(record["longitude"]), int(record["total"])
            )

            cursor.execute('''
                INSERT OR IGNORE INTO youbike_stations (
                    sno, sna, sarea, ar, sareaen, snaen, aren, latitude, longitude, capacity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', station_info)

            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status_info = (
                record["sno"], current_timestamp,
                int(record.get("available_rent_bikes", 0)),
                int(record.get("available_return_bikes", 0))
            )

            cursor.execute('''
                INSERT OR IGNORE INTO youbike_status (
                    sno, mday, available_rent_bikes, available_return_bikes
                ) VALUES (?, ?, ?, ?)
            ''', status_info)

        conn.commit()
        logging.info("YouBike data stored successfully.")

    except requests.RequestException as e:
        logging.error(f"Error fetching YouBike data: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Weather data fetch function
def fetch_weather_data():
    url = "https://www.cwa.gov.tw/V8/E/W/OBS_County.html?ID=63"
    # options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

    # # Specify the path to the ChromeDriver executable
    # driver = webdriver.Chrome(service=ChromeService(executable_path='/usr/local/bin/chromedriver'), options=options)

    try:
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//tbody[@id='stations']/tr"))
        )

        tbody = driver.find_element(By.ID, "stations")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            station = row.find_element(By.TAG_NAME, "th").text.strip()
            cells = row.find_elements(By.TAG_NAME, "td")

            data = {
                "observe_time": None,
                "temperature": None,
                "weather": None,
                "wind_direction": None,
                "wind_speed": None,
                "gust": None,
                "visibility": None,
                "humidity": None,
                "pressure": None,
                "rainfall": None,
                "sunshine": None,
            }

            for cell in cells:
                header = cell.get_attribute("headers")
                value = cell.text.strip()
                if value in ["-", "Unavailable", "Without Observation", "<1", "TRACE"]:
                    value = None

                if header == "OBS_Time":
                    data["observe_time"] = value
                elif header == "temp":
                    data["temperature"] = float(value) if value else None
                elif header == "weather":
                    data["weather"] = cell.accessible_name
                elif header == "w-1":
                    data["wind_direction"] = value
                elif header == "w-2":
                    data["wind_speed"] = float(value) if value else None
                elif header == "w-3":
                    data["gust"] = float(value) if value else None
                elif header == "visible":
                    data["visibility"] = value
                elif header == "hum":
                    data["humidity"] = int(value) if value else None
                elif header == "pre":
                    data["pressure"] = float(value) if value else None
                elif header == "rain":
                    data["rainfall"] = float(value) if value else None
                elif header == "sunlight":
                    data["sunshine"] = value

            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT OR IGNORE INTO weather (
                    station_name, observe_time, temperature, weather, wind_direction, 
                    wind_speed, gust, visibility, humidity, pressure, rainfall, sunshine
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                station,
                current_timestamp,
                data["temperature"],
                data["weather"],
                data["wind_direction"],
                data["wind_speed"],
                data["gust"],
                data["visibility"],
                data["humidity"],
                data["pressure"],
                data["rainfall"],
                data["sunshine"]
            ))

        conn.commit()
        logging.info("Weather data stored successfully.")

    except Exception as e:
        logging.error(f"Error during weather data scraping: {e}")


def clean_tmp():
    tmp_path = "/tmp"  # Or your custom temp directory
    try:
        shutil.rmtree(tmp_path, ignore_errors=True)
        os.makedirs(tmp_path, exist_ok=True)
        logging.info("Temporary files cleaned up.")
    except Exception as e:
        logging.error(f"Error cleaning temp files: {e}")

# Scheduling functions
def schedule_jobs():
    """ Schedules periodic data collection tasks. """
    schedule.every(10).minutes.do(fetch_youbike_data)
    schedule.every(10).minutes.do(fetch_weather_data)
    schedule.every().day.at("00:00").do(clean_tmp)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Avoids excessive CPU usage

# Main execution
if __name__ == "__main__":
    fetch_youbike_data()  # Run immediately once
    fetch_weather_data()  # Run immediately once
    schedule_jobs()  # Start periodic execution
