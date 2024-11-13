import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

# Connect to the database
conn = sqlite3.connect('youbike_data.db')

# Load data into a DataFrame
def load_data():
    query = '''
        SELECT sno, sna, mday, available_rent_bikes, available_return_bikes, latitude, longitude
        FROM youbike_data
        ORDER BY mday
    '''
    df = pd.read_sql_query(query, conn)
    # Convert mday to datetime for easier plotting
    df['mday'] = pd.to_datetime(df['mday'])
    return df

# Visualization 1: Available Bikes Over Time for Selected Stations
def plot_available_bikes(df, station_ids):
    plt.figure(figsize=(12, 6))
    for station in station_ids:
        station_data = df[df['sno'] == station]
        plt.plot(station_data['mday'], station_data['available_rent_bikes'], label=station_data['sna'].iloc[0])
    
    plt.xlabel("Time")
    plt.ylabel("Available Rent Bikes")
    plt.title("Available Bikes Over Time")
    plt.legend(loc="upper right")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Visualization 2: Station Heatmap of Bike Availability
def plot_station_availability(df):
    # Group data by station and get the latest available bike count
    latest_data = df.sort_values('mday').groupby('sno').last().reset_index()
    
    plt.figure(figsize=(10, 8))
    plt.scatter(latest_data['longitude'], latest_data['latitude'], 
                s=latest_data['available_rent_bikes'] * 5,  # Scale marker size
                c=latest_data['available_rent_bikes'], cmap='viridis', alpha=0.7)
    
    plt.colorbar(label="Available Rent Bikes")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Bike Availability by Station")
    plt.show()

# Load data from database
df = load_data()

# Plot available bikes over time for selected stations (replace with station IDs you want to track)
plot_available_bikes(df, station_ids=['500101001', '500101002'])

# Plot station availability as a heatmap
plot_station_availability(df)
