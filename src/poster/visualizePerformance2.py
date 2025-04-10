import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Check available files in directory
print("Available files:", os.listdir("./results/"))

# Load training times data
training_times_file = "./results/training_times_processed_data_all_stations_weather_500101005.csv"  # Adjust filename if needed
training_times_df = pd.read_csv(training_times_file)

# Separate training and inference times
training_df = training_times_df[~training_times_df["Model"].str.contains("Inference")]
inference_df = training_times_df[training_times_df["Model"].str.contains("Inference")]

# Plot Training Times
plt.figure(figsize=(10, 5))
sns.barplot(x="Model", y="Time (s)", data=training_df, hue="Model", palette="Blues", legend=False)
plt.title("Model Training Time (s)")
plt.xticks(rotation=45)
plt.ylabel("Time (s)")
plt.savefig("./results/training_times_comparison.png", dpi=300, bbox_inches="tight")
print("Training time plot saved as 'training_times_comparison.png'")

# Plot Inference Times (Log Scale)
plt.figure(figsize=(10, 5))
sns.barplot(x="Model", y="Time (s)", data=inference_df, hue="Model", palette="Greens", legend=False)
plt.title("Model Inference Time (s)")
plt.xticks(rotation=45)
plt.ylabel("Time (s)")
plt.yscale("log")  # Log scale for better visibility of small values
plt.savefig("./results/inference_times_comparison.png", dpi=300, bbox_inches="tight")
print("Inference time plot saved as 'inference_times_comparison.png'")

# Load performance data
performance_file = "./results/model_comparison_processed_data_all_stations_weather_500101005.csv"  # Adjust filename if needed
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