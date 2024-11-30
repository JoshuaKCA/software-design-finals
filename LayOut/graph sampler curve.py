import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import random

# Generate sample data for wattage (simulated data for demonstration)
hours = np.array([hour for hour in range(24)])
wattage = np.array([np.sin(hour / 3.0) + random.uniform(-0.1, 0.1) for hour in hours])  # Simulated sinusoidal data

# Create a smooth curve using spline interpolation
x_smooth = np.linspace(hours.min(), hours.max(), 300)  # More points for a smoother curve
spl = make_interp_spline(hours, wattage, k=3)  # Cubic spline
wattage_smooth = spl(x_smooth)

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(x_smooth, wattage_smooth, label="Wattage", color="orange", linewidth=2)
plt.fill_between(x_smooth, wattage_smooth, color="orange", alpha=0.3)  # Filled area under the curve
plt.axhline(0, color="gray", linewidth=0.5)  # Zero line

# Set labels and title
plt.xlabel("Time (24-hour format)")
plt.ylabel("Power (kW)")
plt.title("House Wattage Throughout the Day")
plt.ylim(-1.5, 1.5)  # Set the y-axis limits to match the example
plt.legend(["Wattage"], loc="upper right")

# Customize the x-axis ticks
plt.xticks(hours, [f"{hour:02d}:00" for hour in hours], rotation=45)

# Show the plot
plt.tight_layout()
plt.show()