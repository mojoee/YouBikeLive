#!/bin/bash

# Define the path to the configuration file and the script to run
CONFIG_FILE="src/config.py"
SCRIPT_TO_RUN="src/instance_generator_forecast.py"

# Define the start date
START_DATE="2025-03-24"

# Define the array of inventory strategies to loop through
INVENTORY_STRATEGIES=("min_peak" "min_total" "nochange" "proportional")

# Loop through 7 days (1 week)
for i in {0..6}; do
    # Calculate the current date by adding $i days to the START_DATE
    CURRENT_DATE=$(date -I -d "$START_DATE + $i days")
    
    # Update the instance_start value in the config file
    sed -i "/instance_start/c\    instance_start = \"$CURRENT_DATE 00:00:00\"" "$CONFIG_FILE"
    
    # Loop through inventory strategies
    for inv_strat in "${INVENTORY_STRATEGIES[@]}"; do
        # Update the inventory strategy in the config file
        sed -i "/inventory_strategy/c\    inventory_strategy = \"$inv_strat\"" "$CONFIG_FILE"
        
        # Log the current configuration
        echo "Processing: Date=$CURRENT_DATE, Inventory=$inv_strat"
        
        # Run the Python script
        python3 "$SCRIPT_TO_RUN"
        
        # Check if the script ran successfully
        if [ $? -ne 0 ]; then
            echo "Error: Script execution failed with Date=$CURRENT_DATE, Inventory=$inv_strat. Exiting."
            exit 1
        fi
    done
done

echo "All combinations processed successfully."
