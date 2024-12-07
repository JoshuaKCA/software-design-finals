import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import make_interp_spline
import random

customtkinter.set_default_color_theme("green")
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Insert Window title")
        self.state('zoomed')

        # Configure grid layout for the main window
        self.configure_grid()

        # Create UI components
        self.create_header()
        self.create_sidebar()
        self.create_main_content()

        # Create tab buttons and contents
        self.tab_buttons = []
        self.tab_contents = []
        self.create_tabs()

        # Show the first tab by default
        self.show_tab(0)
#METHODS
#CREATE GENERAL LAYOUT (Content Placement: Header, Main Content, Side bar) ------------------------------------------------------------------------------------------------------------------------------------------------------
    def configure_grid(self):
        """Configure the grid layout for the main window."""
        # Set the row and column weights to allow resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def create_header(self):
        """Create the header section."""
        # Create a frame for the header with specific styling
        self.header = customtkinter.CTkFrame(self, fg_color="#ffffff", height=65, corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.header.grid_propagate(False)  # Prevent the frame from resizing based on its content

    def create_sidebar(self):
        """Create the sidebar with logo and tab buttons."""
        # Create a frame for the sidebar with specific styling
        self.sidebar = customtkinter.CTkFrame(self, fg_color="black", width=250, corner_radius=0)
        self.sidebar.grid(row=1, column=0, rowspan=1, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)  # Center the buttons

        # Add logo icon to the sidebar
        self.add_logo_to_sidebar()

    def add_logo_to_sidebar(self):
        """Add a logo image to the sidebar."""
        # Load and create an image for the logo
        png_image = customtkinter.CTkImage(
            light_image=Image.open("svg_files\Lightbulb 02.png"),
            dark_image=Image.open("svg_files\Lightbulb 02.png"),
            size=(50, 50)
        )
        # Add the image to a label and place it in the sidebar
        self.image_label = customtkinter.CTkLabel(self.sidebar, image=png_image, text="")
        self.image_label.grid(row=0, column=0, pady=10)

    def create_main_content(self):
        """Create the main content area."""
        # Create a frame for the main content with specific styling
        self.main_content = customtkinter.CTkFrame(self, fg_color="#f0f0f0", corner_radius=0)
        self.main_content.grid(row=1, column=1, sticky="nsew")

    def create_tabs(self):
        """Create tab buttons and their corresponding content."""
        # Define tab names with "Dashboard" and "Appliance" as specific tabs
        tab_names = ["Dashboard", "2", "Appliance", "Notifications"]
        for index, name in enumerate(tab_names):
            self.create_tab_button(name, index)
            self.create_tab_content(index)

    def create_tab_button(self, text, index):
        """Create a button for each tab in the sidebar. (Constructing the tab buttons)"""
        # Create a button for the tab and add it to the sidebar
        button = customtkinter.CTkButton(
            self.sidebar, text=text, command=lambda: self.show_tab(index), width=200, height=50, corner_radius=0
        )
        button.grid(row=index + 1, column=0,  pady=1, sticky="ew") 
        self.tab_buttons.append(button)

    def create_tab_content(self, index):
        """Create content for each tab."""
        # Create a frame for the tab content
        frame = customtkinter.CTkFrame(self.main_content, corner_radius=0, fg_color="#f0f0f0")

        if index == 0:  # Dashboard Page
            self.create_dashboard_content(frame)
        elif index == 2:  # Appliance Page
            self.create_appliance_content(frame)
        elif index == 3: # Notification Page
            self.create_notification_tab(frame)
        else:
            # Add a label to the frame for other tabs
            label = customtkinter.CTkLabel(frame, text=f"Content for Tab {index + 1}")
            label.pack(padx=20, pady=20)

        self.tab_contents.append(frame)

#DASHBOARD PAGE --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #Line Graph Widgets
    def create_dashboard_content(self, frame):
        """Create content for the Dashboard tab."""
        dashboard_label = customtkinter.CTkLabel(frame, text="DASHBOARD", text_color='black', font=('Helvetica', 24))
        dashboard_label.pack(padx=30, pady=(15, 0), anchor='nw')

        # Create line graph content
        self.create_line_graph_frame(frame)

        # Create a container frame to hold both the goal tracker and notification shortcut frames
        bottom_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
        bottom_frame.pack(side='bottom', anchor='center', expand=False, padx=70, pady=15, fill='x')

        # Create the goal tracker content
        self.create_goal_tracker_frame(bottom_frame)
        # Create the notification shortcut content
        self.create_notification_shortcut_frame(bottom_frame)

    def create_line_graph_frame(self, parent):
        """Create a frame to hold line graphs."""
        # Create a frame for the line graph
        graph_frame = customtkinter.CTkFrame(parent, width=880, height=461, fg_color='white', border_width=1, border_color='#b2b2b2', corner_radius=20)
        graph_frame.pack(side='top', anchor='nw', expand=False, padx=70, pady=(15,0))
        graph_frame.pack_propagate(False)   

        # Create button frame for graph selection
        button_frame = customtkinter.CTkFrame(graph_frame, width=600, height=30, fg_color='transparent')
        button_frame.pack(side='top', anchor='w', fill=None, padx=20, pady=(30,20))
        button_frame.pack_propagate(False)

        # Graph selection buttons
        self.create_graph_buttons(button_frame, graph_frame)

        # Show first graph by default
        self.switch_graph(0, graph_frame)
    def create_graph_buttons(self, parent, graph_frame):
            """Create buttons to switch between different graphs."""
            self.active_graph_button = 0
            active_color = "black" 
            active_text_color = "#7ed957"
            inactive_color = "#b2b2b2"
            inactive_text_color='white'
            
            def toggle_button(button_index, button_list):
                    self.active_graph_button = button_index
                    for idx, btn in enumerate(button_list):
                        is_active = idx == button_index
                        btn.configure(
                            fg_color=active_color if is_active else inactive_color,
                            text_color=active_text_color if is_active else inactive_text_color
                        )
                    self.switch_graph(button_index, graph_frame)

            graph1_btn = customtkinter.CTkButton(
                parent, 
                text="Day",
                width=100,
                height=30,
                fg_color=active_color,
                corner_radius=0
            )
            
            graph2_btn = customtkinter.CTkButton(
                parent,
                text="Month",
                width=100,
                height=30,
                fg_color=inactive_color,
                corner_radius=0
            )
            
            graph3_btn = customtkinter.CTkButton(
                parent,
                text="Year",
                width=100,
                height=30,
                fg_color=inactive_color,
                corner_radius=0
            )

            buttons = [graph1_btn, graph2_btn, graph3_btn]
            
            graph1_btn.configure(command=lambda: toggle_button(0, buttons))
            graph2_btn.configure(command=lambda: toggle_button(1, buttons))
            graph3_btn.configure(command=lambda: toggle_button(2, buttons))

            graph1_btn.pack(side='left',  fill='y')
            graph2_btn.pack(side='left',  fill='y')
            graph3_btn.pack(side='left',  fill='y')

    def create_line_graph(self, parent):
        """Create a sinusoidal wattage line graph."""
        # Generate sample data for wattage (simulated data for demonstration)
        hours = np.array([hour for hour in range(24)])
        wattage = np.array([np.sin(hour / 3.0) + random.uniform(-0.1, 0.1) for hour in hours])  # Simulated sinusoidal data

        # Create a smooth curve using spline interpolation
        x_smooth = np.linspace(hours.min(), hours.max(), 300)  # More points for a smoother curve
        spl = make_interp_spline(hours, wattage, k=3)  # Cubic spline
        wattage_smooth = spl(x_smooth)

        # Create a matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(x_smooth, wattage_smooth, label="Wattage", color="orange", linewidth=2)
        ax.fill_between(x_smooth, wattage_smooth, color="orange", alpha=0.3)  # Filled area under the curve
        ax.axhline(0, color="gray", linewidth=0.5)  # Zero line

        ax.spines['top'].set_visible(False)  # Remove the top border
        ax.spines['right'].set_visible(False)

        ax.set_xlim(x_smooth[0], x_smooth[-1]) 

        # Set labels and title
        ax.set_ylabel("Power (kW)")
        ax.set_ylim(0, 1.5)  # Set the y-axis limits to match the example
        ax.legend(["Wattage"], loc="upper right")

        # Customize the x-axis ticks
        ax.set_xticks(hours)
        ax.set_xticklabels([f"{hour:02d}:00" for hour in hours], rotation=45)

        # Embed the plot in the Tkinter application
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=2, pady=2)

        plt.tight_layout()
        plt.close(fig)

    def switch_graph(self, graph_index, parent):
        """Switch between different graphs."""
        # Clear existing graph widgets
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        # Create the selected graph
        if graph_index == 0:
            self.create_line_graph(parent)
        elif graph_index == 1:
            self.create_bar_graph_for_month(parent)
        elif graph_index == 2:
            self.create_bar_graph_for_year(parent)

    def create_bar_graph_for_month(self, parent):
        """Create a bar graph for the month."""
        # Define data for the bar graph
        x = list(range(1, 32))
        y = [23, 45, 56, 78, 43] + [0] * 26

        # Create a matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x, y)

        # Set labels and title
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Sample Bar Graph')
        ax.tick_params(labelsize=8)

        # Embed the plot in the Tkinter application
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=2, pady=2)
        plt.tight_layout()
        plt.close(fig)

    def create_bar_graph_for_year(self, parent):
        """Create a bar graph for the year."""
        # Define data for the bar graph
        x = list(range(1, 13))
        y = [2, 5, 3, 8, 6, 7, 1, 4, 9, 5, 0, 0]

        # Create a matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x, y)

        # Set labels and title
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Sample Bar Graph')
        ax.tick_params(labelsize=8)

        # Embed the plot in the Tkinter application
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=2, pady=2)
        plt.tight_layout()
        plt.close(fig)

    def create_goal_tracker_frame(self, parent):
        """Create the goal tracker frame."""
        goal_frame = customtkinter.CTkFrame(parent, width=360, height=180, corner_radius=20, fg_color='white', border_width=1, border_color='#b2b2b2',)
        goal_frame.pack(side='left', anchor='center', expand=True, fill='none', padx=(70, 15), pady=15)
        goal_frame.pack_propagate(True)

        # Configure grid weights if needed
        goal_frame.grid_rowconfigure(0, weight=0)
        goal_frame.grid_rowconfigure(1, weight=0)
        goal_frame.grid_columnconfigure(0, weight=1)
        goal_frame.grid_columnconfigure(1, weight=1)

        self.create_goal_tracker_content(goal_frame)

        # Debugging: Print the actual size after layout
        self.after(100, lambda: print("Notification Frame Size:", goal_frame.winfo_width(), goal_frame.winfo_height()))

    def create_goal_tracker_content(self, frame):
        """Create content for the goal tracker frame."""
        accumulated_consumption = 120.50
        set_goal = 450.80

        image_placeholder = customtkinter.CTkFrame(frame, fg_color="green", height=100, width=100, corner_radius=50)
        image_placeholder.grid(row=0, rowspan=2, column=0, padx=15, pady=10, sticky='w')

        goal_tracker_label = customtkinter.CTkLabel(frame, 
            text=" Monthly Goal Tracker ", 
            font=('Arial', 17, 'bold'), 
            wraplength=250, 
            justify='center', 
            text_color="black"
        )

        goal_tracker_label.grid(row=0, column=1, padx=(0,15), pady=(5,0), sticky='sew')

        tracker_slash_label = customtkinter.CTkLabel(frame, 
            text=f"P {accumulated_consumption} / P {set_goal}", 
            font=('Arial', 20, 'bold'), 
            wraplength=200, 
            justify='center', 
            text_color='#8e8e8e'
        )

        tracker_slash_label.grid(row=1, column=1, padx=(0,15), sticky='new')


    def create_notification_shortcut_frame(self, parent):
        notification_shortcut_frame = customtkinter.CTkFrame(parent, width=350, height=120, corner_radius=20, fg_color='white', border_width=1, border_color='#b2b2b2',)
        notification_shortcut_frame.pack(side='left', anchor='center', expand=False, fill='none', padx=70, pady=15)
        notification_shortcut_frame.pack_propagate(False)
        
        # Configure grid weights
        notification_shortcut_frame.grid_rowconfigure(0, weight=0)
        notification_shortcut_frame.grid_rowconfigure(1, weight=1)
        notification_shortcut_frame.grid_columnconfigure(0, weight=0)
        notification_shortcut_frame.grid_columnconfigure(1, weight=1)

        self.create_notification_shortcut_frame_content(notification_shortcut_frame)

        # Debugging: Print the actual size after layout
        self.after(100, lambda: print("Notification Frame Size:", notification_shortcut_frame.winfo_width(), notification_shortcut_frame.winfo_height()))
        
    def create_notification_shortcut_frame_content(self, frame):
        """Create content for the notification shortcut frame."""
        image_placeholder = customtkinter.CTkFrame(frame, fg_color="green", height=100, width=100, corner_radius=50)
        image_placeholder.grid(row=0, rowspan=2, column=0, padx=15, pady=10, sticky='w')

        notice_label = customtkinter.CTkLabel(frame, text="Notification", font=('Arial', 18, 'bold'), text_color="black")
        notice_label.grid(row=0, column=1, padx=5, pady=(15,0), sticky='w')

        notice_content = customtkinter.CTkLabel(frame, 
            text="Your electricity bill is due on 20th of this month. Please pay it on time.",
             font=('Arial', 14), wraplength=200, justify='left', text_color='#8e8e8e')

        notice_content.grid(row=1, column=1, padx=(5,10), sticky='nw')


#APPLIANCE PAGE ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def create_appliance_content(self, frame):
        """Create content for the Appliance tab."""
       
        # Add additional widgets for the Appliance page here
        appliance_label = customtkinter.CTkLabel(frame, text="Appliances", text_color='black', font=('Arial', 16,'bold'))
        appliance_label.pack(padx=20, pady=5, anchor='nw')

        self.create_appliance_manager(frame)

    def create_appliance_manager(self, parent):
        """Create the appliance manager interface."""
        # Create control panel and appliance list
        self.create_control_panel(parent)
        self.create_appliance_list(parent)

    def create_control_panel(self, parent):
        """Create the control panel for managing appliances added."""
        # Create a frame for the control panel
        control_frame = customtkinter.CTkFrame(parent   )
        control_frame.pack(fill='x', padx=10, pady=5)

        # Add Appliance Button
        add_btn = customtkinter.CTkButton(control_frame, text="Add Appliance", command=self.add_appliance_dialog, height=40)
        add_btn.pack(side='left', padx=(0,5))

        # Search Frame
        search_frame = customtkinter.CTkFrame(control_frame)
        search_frame.pack(side='left', padx=5)
        search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Search appliances...", height=40, width=400)
        search_entry.pack(side='left', padx=5)
        search_btn = customtkinter.CTkButton(search_frame, text="Search", height=40)
        search_btn.pack(side='left')

        # Sort Dropdown
        sort_label = customtkinter.CTkLabel(control_frame, text="Sort by:")
        sort_options = ["Wattage", "State (On/Off)", "Alphabetical"]
        sort_var = customtkinter.StringVar(value="Sort by...")
        sort_menu = customtkinter.CTkOptionMenu(control_frame, values=sort_options, variable=sort_var, height=40)
        sort_menu.pack(side='right', padx=0)

    def create_appliance_list(self, parent):
        """Create a scrollable list to display appliances."""
        # Create a scrollable frame for the appliance list
        list_frame = customtkinter.CTkScrollableFrame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

    def add_appliance_dialog(self):
        """Open a dialog to add a new appliance."""
        # Create a dialog window for adding appliances
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Add Appliance")
        dialog.geometry("400x300")

        # Name Entry
        name_label = customtkinter.CTkLabel(dialog, text="Appliance Name:")
        name_label.pack(pady=5)
        name_entry = customtkinter.CTkEntry(dialog)
        name_entry.pack(pady=5)

        # Wattage Frame
        wattage_frame = customtkinter.CTkFrame(dialog)
        wattage_frame.pack(pady=10)

        wattage_entry = customtkinter.CTkEntry(wattage_frame, placeholder_text="Wattage")
        wattage_entry.pack(side='left', padx=5)

        units = ["W", "kW", "mW"]
        unit_var = customtkinter.StringVar(value="W")
        unit_menu = customtkinter.CTkOptionMenu(wattage_frame, values=units, variable=unit_var)
        unit_menu.pack(side='left')

        # Save Button
        save_btn = customtkinter.CTkButton(dialog, text="Save Appliance")
        save_btn.pack(pady=20)

    def create_appliance_item(self, list_frame, appliance_data):
        """Create a UI item for each appliance."""
        # Create a frame for each appliance item
        item_frame = customtkinter.CTkFrame(list_frame)
        item_frame.pack(fill='x', pady=2)

        # Appliance Name
        name_label = customtkinter.CTkLabel(item_frame, text=appliance_data['name'])
        name_label.pack(side='left', padx=5)

        # Control Buttons Frame
        btn_frame = customtkinter.CTkFrame(item_frame)
        btn_frame.pack(side='right')

        # Control Buttons
        self.create_control_buttons(btn_frame)

    def create_control_buttons(self, parent):
        """Create control buttons for each appliance item."""
        # Create buttons for controlling appliances
        toggle_btn = customtkinter.CTkButton(parent, text="ON/OFF", width=70)
        toggle_btn.pack(side='right', padx=2)

        schedule_btn = customtkinter.CTkButton(parent, text="Schedule", width=70)
        schedule_btn.pack(side='right', padx=2)

        edit_btn = customtkinter.CTkButton(parent, text="Edit", width=70)
        edit_btn.pack(side='right', padx=2)

        delete_btn = customtkinter.CTkButton(parent, text="Delete", width=70)
        delete_btn.pack(side='right', padx=2)


    def show_tab(self, index):
        """Display the content of the selected tab."""
        # Show the selected tab and hide others
        for i, frame in enumerate(self.tab_contents):
            if i == index:
                frame.grid(row=0, column=0, sticky="nsew", in_=self.main_content)
            else:
                frame.grid_forget()

        # Configure main_content grid weights
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        self.update_idletasks()

#NOTIFICATION PAGE ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def create_notification_tab(self, frame):
        """Create content for the Notification tab."""
        notification_label = customtkinter.CTkLabel(frame, text="NOTIFICATION", text_color='black', font=('Helvetica', 24))
        notification_label.pack(padx=20, pady=(15, 0), anchor='nw')
        
        notifications_frame = customtkinter.CTkFrame(frame, fg_color="#e0e0e0", width=760, height=540, corner_radius=20)
        notifications_frame.pack(side='top', anchor='nw', expand=False, padx=70, pady=(15,50))
        notifications_frame.pack_propagate(False)
        
        # Configure grid layout for notifications_frame
        notifications_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        # Add "Sort by:" label
        sort_by_label = customtkinter.CTkLabel(notifications_frame, text="Sort by:", text_color='black', font=('Helvetica', 24))
        sort_by_label.grid(row=0, column=0, padx=(20,0), pady=(20,0), sticky='w')
        
        # Add combo box next to the label
        sort_by_combobox = customtkinter.CTkComboBox(notifications_frame, state="readonly", values=["Latest", "Priority"], font=('Helvetica', 12))
        sort_by_combobox.grid(row=0, column=1, padx=(0,0), pady=(20,0), sticky='w')
        
        # Add another label and combo box on the upper right part of notifications_frame
        filter_by_label = customtkinter.CTkLabel(notifications_frame, text="Filter by:", text_color='black', font=('Helvetica', 24))
        filter_by_label.grid(row=0, column=2, padx=(10,0), pady=(20,0), sticky='e')
        
        filter_by_combobox = customtkinter.CTkComboBox(notifications_frame, state="readonly", values=["All", "Unread", "Read"], font=('Helvetica', 12))
        filter_by_combobox.grid(row=0, column=3, padx=(0,20), pady=(20,0), sticky='e')
        
        notifications_2frame = customtkinter.CTkScrollableFrame(notifications_frame, fg_color="white", width=760, height=540, corner_radius=15)
        notifications_2frame.grid(row=1, column=0, columnspan=4, padx=15, pady=(25,15), sticky='nsew')

        # Add hardcoded notifications
        for i in range(5):
            notification = customtkinter.CTkLabel(notifications_2frame, text=f"Notification {i+1}", text_color='black', font=('Helvetica', 12))
            notification.pack(pady=5, anchor='nw')
        

if __name__ == "__main__":
    app = App()
    app.mainloop()