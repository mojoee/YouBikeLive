#!/bin/bash

# Define the path to the configuration file and the script to run
CONFIG_FILE="src/config.py"
SCRIPT_TO_RUN="src/instance_generator_forecast.py"

# Define the start date
START_DATE="2024-12-28"

# Loop through 7 days (1 week)
for i in {0..6}; do
    # Calculate the current date by adding $i days to the START_DATE
    CURRENT_DATE=$(date -I -d "$START_DATE + $i days")

    # Update the instance_start value in the config file
    sed -i "/instance_start/c\    instance_start = \"$CURRENT_DATE 00:00:01\"" "$CONFIG_FILE"

    # Log the change
    echo "Updated instance_start to: $CURRENT_DATE 00:00:01"

    # Run the Python script
    python "$SCRIPT_TO_RUN"

    # Check if the script ran successfully
    if [ $? -ne 0 ]; then
        echo "Error: Script execution failed on $CURRENT_DATE. Exiting."
        exit 1
    fi

done

echo "All days processed successfully."
