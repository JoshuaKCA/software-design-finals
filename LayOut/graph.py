import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import random

# Generate sample data for wattage (simulated data for demonstration)
hours = [f"{hour:02d}:00" for hour in range(24)]
wattage = [random.uniform(-0.5, 1.5) for _ in range(24)]  # Random wattage values between -0.5 and 1.5 kW

# Create the main window
root = tk.Tk()
root.title("House Wattage Throughout the Day")
root.geometry("800x500")

# Create a Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(hours, wattage, label="Wattage", color="orange", linewidth=2)
ax.fill_between(hours, wattage, color="orange", alpha=0.3)  # Filled area under the curve
ax.axhline(0, color="gray", linewidth=0.5)  # Zero line

# Set labels and title
ax.set_xlabel("Time (24-hour format)")
ax.set_ylabel("Power (kW)")
ax.set_title("House Wattage Throughout the Day")
ax.set_ylim(-0.6, 1.6)  # Set the y-axis limits to match the example
ax.legend(["AC Output", "Meter Power", "Load Power"], loc="upper right")

# Customize the x-axis ticks
plt.xticks(rotation=45)

# Integrate the Matplotlib figure into Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Run the Tkinter event loop
root.mainloop()
