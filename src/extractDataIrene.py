import sqlite3
import pandas as pd

# Path to your SQLite database
db_path = "./youbike_data.db"

# Station ID to query
station_id = '500101027'

# SQL query
query = f"""
SELECT *
FROM 
    youbike_data
WHERE 
    sno = '{station_id}'
ORDER BY 
    mday ASC;
"""

# Connect to the database and execute the query
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query(query, conn)

# Display the result
print(df)

name = "NTUSTBackGate"
# Optionally save to a CSV
df.to_csv(f"station_{name}_bikes_over_time.csv", index=False)
