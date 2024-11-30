import tkinter as tk
from tkinter import Canvas

def create_lightning(canvas, x, y, size):
    # Draw a simple lightning bolt shape
    points = [
        x, y,
        x + size * 0.3, y + size * 0.5,
        x + size * 0.2, y + size * 0.5,
        x + size * 0.5, y + size,
        x + size * 0.3, y + size * 0.5,
        x + size * 0.4, y + size * 0.5
    ]
    canvas.create_polygon(points, fill='green', outline='green')

def main():
    root = tk.Tk()
    root.title("Daily Generation")

    # Create a frame with rounded corners
    frame = tk.Frame(root, bg='#f8f8e8', bd=2, relief='solid')
    frame.pack(padx=10, pady=10)

    # Create a canvas for the lightning icon
    canvas = Canvas(frame, width=50, height=50, bg='#f8f8e8', highlightthickness=0)
    canvas.grid(row=0, column=0, padx=10, pady=10)
    create_lightning(canvas, 10, 10, 30)

    # Create labels for the text
    title_label = tk.Label(frame, text="Daily Generation", font=("Arial", 10, "bold"), bg='#f8f8e8')
    title_label.grid(row=0, column=1, sticky='w')

    value_label = tk.Label(frame, text="5.9 kW/h", font=("Arial", 10), fg='gray', bg='#f8f8e8')
    value_label.grid(row=1, column=1, sticky='w')

    root.mainloop()

if __name__ == "__main__":
    main()