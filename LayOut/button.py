import customtkinter as ctk

# Initialize customtkinter
ctk.set_appearance_mode("dark")  # Optional: Dark mode
ctk.set_default_color_theme("green")  # Optional: Green theme

# Create main window
root = ctk.CTk()
root.geometry("300x100")

# Create a frame to hold the buttons
button_frame = ctk.CTkFrame(root, fg_color="gray80", corner_radius=10)
button_frame.pack(pady=20, padx=20, fill="x")

# Function to switch active tab style
def switch_tab(selected_button):
    # Reset all buttons to default style
    for button in buttons:
        button.configure(fg_color="gray80", text_color="gray50")
    
    # Set the selected button style
    selected_button.configure(fg_color="black", text_color="green")

# Create buttons
buttons = [
    ctk.CTkButton(button_frame, text="Daily", width=80, height=30, corner_radius=10, 
                  fg_color="black", text_color="green", command=lambda: switch_tab(buttons[0])),
    ctk.CTkButton(button_frame, text="Weekly", width=80, height=30, corner_radius=10, 
                  fg_color="gray80", text_color="gray50", command=lambda: switch_tab(buttons[1])),
    ctk.CTkButton(button_frame, text="Monthly", width=80, height=30, corner_radius=10, 
                  fg_color="gray80", text_color="gray50", command=lambda: switch_tab(buttons[2]))
]

# Place buttons side by side
for i, button in enumerate(buttons):
    button.grid(row=0, column=i, padx=(0 if i == 0 else 10, 0))

# Run the Tkinter event loop
root.mainloop()
