import sqlite3

# Database paths
db_path = "youbike_data.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# Step 1: Insert unique station data into `youbike_stations`
cursor.execute("""
    INSERT OR IGNORE INTO youbike_stations (sno, sna, sarea, latitude, longitude, capacity)
    SELECT DISTINCT
        sno,
        sna,
        sarea,
        latitude,
        longitude,
        total
    FROM youbike_data
""")
print("Static station data migrated to `youbike_stations`.")

# Step 2: Insert dynamic status data into `youbike_status`
cursor.execute("""
    INSERT OR IGNORE INTO youbike_status (sno, mday, available_rent_bikes, available_return_bikes)
    SELECT
        sno,
        mday AS timestamp,
        available_rent_bikes,
        total - available_rent_bikes AS available_return_bikes
    FROM youbike_data
""")
print("Dynamic status data migrated to `youbike_status`.")

# Commit and close the connection
conn.commit()
conn.close()
print("Data migration completed successfully.")