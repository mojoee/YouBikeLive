import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load performance data
performance_file = "./results/model_comparison_processed_data_all_stations_weather_500101001.csv"
training_times_file = "./results/training_times_processed_data_all_stations_weather_500101005.csv"  # Adjust the filename
performance_df = pd.read_csv(performance_file)

# Define metrics and colors
metrics = ["MAE", "MSE", "MAPE (%)"]
colors = ["Oranges", "Purples", "Reds"]

# Create subplots for each metric
fig, axes = plt.subplots(3, 1, figsize=(10, 15))

def plot_metric(ax, metric, color):
    sns.barplot(x="Model", y=metric, data=performance_df, hue="Model", palette=color, ax=ax, legend=False)
    ax.set_title(f"Model {metric} Comparison")
    ax.set_xticks(range(len(performance_df["Model"])))
    ax.set_xticklabels(performance_df["Model"], rotation=45)
    ax.set_ylabel(metric)

for i, (metric, color) in enumerate(zip(metrics, colors)):
    plot_metric(axes[i], metric, color)

plt.tight_layout()
plt.savefig("./results/performance_comparison.png", dpi=300, bbox_inches="tight")  # Save figure
print("Performance comparison plot saved as 'performance_comparison.png'")
