import sqlite3
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import schedule
import time
from datetime import datetime


# Logging configuration
logging.basicConfig(level=logging.INFO, filename='weather_data_collector.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
db_path = 'youbike_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create weather table if it doesn't exist
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

# Web scraping function
def fetch_weather_data():
    # URL of the weather page
    url = "https://www.cwa.gov.tw/V8/E/W/OBS_County.html?ID=63"
    options = ChromeOptions()
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    
    driver = Chrome(options=options)

    try:
        # Load the webpage
        driver.get(url)

        # Wait for the rows inside the "stations" element to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//tbody[@id='stations']/tr"))
        )

        # Extract the weather data
        tbody = driver.find_element(By.ID, "stations")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            station = row.find_element(By.TAG_NAME, "th").text.strip()
            cells = row.find_elements(By.TAG_NAME, "td")

            # Extract values by matching headers
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

            # Insert weather data into the database
            cursor.execute('''
                INSERT OR IGNORE INTO weather (
                    station_name, observe_time, temperature, weather, wind_direction, 
                    wind_speed, gust, visibility, humidity, pressure, rainfall, sunshine
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                station,
                current_timestamp,  # Use the generated timestamp
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
        logging.error(f"Error during scraping: {e}")
    finally:
        driver.quit()

# Scheduler setup
def job():
    try:
        fetch_weather_data()
    except Exception as e:
        logging.error(f"Scheduled job error: {e}")

schedule.every(10).minutes.do(job)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
