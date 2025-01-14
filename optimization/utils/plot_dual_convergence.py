#!/usr/bin/env python3

import re
import matplotlib.pyplot as plt

logfile = "./results/v4_cb/v12-24-24_b8h_uniform_goal.txt"

# Initialize lists to store the data
times = []
obj1_values = []
obj2_values = []
abs_demands_total = 0

# Open the logfile and read from it line by line
with open(logfile, 'r') as file:
    for line in file:
        # Split the line based on multiple separators (spaces, commas, semicolons, brackets)
        words = re.split(r'[ ,;\[\]]+', line.strip())
        if len(words) > 2 and words[2] == 'sec':
            time = int(words[1])
            obj1 = int(words[6])
            obj2 = int(words[8]) / 60
            times.append(time)
            obj1_values.append(obj1)
            obj2_values.append(obj2)
        if len(words) > 1 and words[0] == 'abs_demands_total:':
            abs_demands_total = int(words[1])

# Create the plot with a specific size
fig, ax1 = plt.subplots(figsize=(8, 6))  # Set the plot size to 8 inches by 6 inches

# Plot the first y-axis
ax1.set_xlabel('Computing time (sec)')
ax1.set_ylabel('Satisfied bike relocations', color='tab:blue')
line1, = ax1.plot(times, obj1_values, color='tab:blue', label='Satisfied bike relocations', zorder=2)
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Add grid to the first y-axis
ax1.grid(True)

# Create a second y-axis
ax2 = ax1.twinx()
ax2.set_ylabel('Makespan (min)', color='tab:red')
line2, = ax2.plot(times, obj2_values, color='tab:red', label='Relocation makespan', zorder=1)
ax2.tick_params(axis='y', labelcolor='tab:red')

# Add grid to the second y-axis
ax2.grid(True)

# Plot first occurrence of the abs_demands_total and annotate the value of t
for t, obj1 in zip(times, obj1_values):
    if obj1 == abs_demands_total:
        vline = ax1.axvline(x=t, color='black', linestyle='--', label='All relocations planned', zorder=3)
        ax1.annotate(f't={t} sec', xy=(t, ax1.get_ylim()[1]), xytext=(t + 50, ax1.get_ylim()[1] * 0.5), horizontalalignment='left')
        break

# Combine the line objects from both axes
lines = [line1, line2, vline]
labels = [line.get_label() for line in lines]

# Add legends
ax1.legend(lines, labels, loc='lower right')

# Add a title
plt.title('Objectives convergence over time')

# Save the figure to a PDF file with tight borders
fig_name = logfile.replace('.txt', '.pdf')
plt.savefig(fig_name, bbox_inches='tight')

# Show the plot
plt.show()