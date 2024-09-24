import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data from the provided file
file_path = 'BERT/url_score.csv'
data = pd.read_csv(file_path)

# Clean up column names (if needed)
data.columns = data.columns.str.strip()

# Extracting data from the dataframe
T = data['T']
T2 = data['T2']
UT = data['UT']
UT1 = data['UT1']
UT2 = data['UT2']

# Scatter plot function with color coding for T2
def plot_scatter_with_color(x, y, color, title, x_label, y_label, color_label=""):
    fig, ax = plt.subplots()

    if color_label:
        scatter = ax.scatter(x, y, c=color, cmap='viridis', edgecolor='k', s=100)
    else:
        scatter = ax.scatter(x, y)
    
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    if color_label:
        # Add color bar to represent T2
        cbar = plt.colorbar(scatter)
        cbar.set_label(color_label)
    
    plt.savefig(f'BERT/url_score/plots/output_{y_label}.pdf', format="pdf")

# Plot scatter plots for UT, UT1, and UT2
plot_scatter_with_color(T, UT, T2, "UT score depending on T and T2, T1=5", "T", "UT", "T2")
plot_scatter_with_color(T, UT1, T2, "UT1 score depending on T, T1=5", "T", "UT1")
plot_scatter_with_color(T, UT2, T2, "UT2 score depending on T and T2, T1=5", "T", "UT2", "T2")
