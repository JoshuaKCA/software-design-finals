import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import make_interp_spline
from datetime import datetime
import time
import matplotlib.dates as mdates
import subprocess

customtkinter.set_default_color_theme("green")

class Appliance:
    def __init__(self, name, wattage, unit, schedule_start, schedule_end,  state='OFF'):
        self.name = name
        self.state = state
        # Convert wattage to watts if the unit is kW
        if unit == "kW":
            self.wattage = wattage * 1000
        else:
            self.wattage = wattage
        self.unit = unit
        self.schedule_start = schedule_start
        self.schedule_end = schedule_end

    def save_to_file(self, filename):
        with open(filename, 'a') as file:
            file.write(f"{self.name},{self.wattage},{self.unit},{self.schedule_start},{self.schedule_end},{self.state}\n")
            
    def load_from_file(cls, filename):
        appliances = []
        with open(filename, 'r') as file:
            for line in file:
                name, wattage, unit, schedule_start, schedule_end, state = line.strip().split(',')
                wattage = float(wattage)
                appliances.append(cls(name, wattage, unit, schedule_start, schedule_end, state))
        return appliances
    
    def display_wattage(self):
        if self.unit == "kW":
            display_value = self.wattage / 1000
        else:
            display_value = self.wattage
        return f"{display_value}"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("EnerCheck")
        self.state('zoomed')
        self.geometry("1600x900")

        self.monthly_goal = None

        """Appliance List"""
        self.appliances = []
        self.appliance_buttons = {}

        self.accumulated_wattage = 0
        self.start_time = time.time()
        
        # Initialize data for plotting
        self.x_data = []
        self.y_data = []
        self.daily_wattage = [0] * 31
        self.monthly_wattage = [0] * 12

        self.start_monthly_cost_tracking()
        
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
        self.header.grid(row=0, column=1, columnspan=1, sticky="nsew")
        self.header.grid_propagate(False)  # Prevent the frame from resizing based on its content

    def create_sidebar(self):
        """Create the sidebar with logo and tab buttons."""
        # Create a frame for the sidebar with specific styling
        self.sidebar = customtkinter.CTkFrame(self, fg_color="black", width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)  # Center the buttons


        # Logout button
        logout_btn = customtkinter.CTkButton(self, text="Logout", command=self.logout)
        logout_btn.grid(row=11, column=0, padx=20, pady=20, sticky="s")

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
        tab_names = ["Dashboard", "Appliance", "Notifications", "Settings"]
        for index, name in enumerate(tab_names):
            self.create_tab_button(name, index)
            self.create_tab_content(index)

    def create_tab_button(self, text, index):
        """Create a button for each tab in the sidebar. (Constructing the tab buttons)"""
        # Create a button for the tab and add it to the sidebar
        button = customtkinter.CTkButton(
            self.sidebar, text=text, font = ('Arial', 14), command=lambda: self.show_tab(index), width=200, height=60, corner_radius=0
        )
        button.grid(row=index + 1, column=0,  pady=1, sticky="ew") 
        self.tab_buttons.append(button)

    def create_tab_content(self, index):
        """Create content for each tab."""
        # Create a frame for the tab content
        frame = customtkinter.CTkFrame(self.main_content, corner_radius=0, fg_color="#f0f0f0")

        if index == 0:  # Dashboard Page
            self.create_dashboard_content(frame)
        elif index == 1:  # Appliance Page
            self.create_appliance_content(frame)
        elif index == 2: # Notification Page
            self.create_notification_tab(frame)
        elif index == 3: # Notification Page
            self.create_settings_tab(frame)
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

    # Create a container frame to hold both the line graph and appliance control frames
        top_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(side='top', anchor='center', expand=False, padx=30, pady=(15, 0), fill='x')

        # Create line graph content
        self.create_line_graph_frame(top_frame)

        # Create appliance controls beside the line graph
        self.create_appliance_controls_frame(top_frame)

        # Create a container frame to hold both the goal tracker and notification shortcut frames
        bottom_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
        bottom_frame.pack(side='bottom', anchor='center', expand=False, padx=70, pady=15, fill='x')

        # Create the goal tracker content
        self.create_goal_tracker_frame(bottom_frame)
         # Create the cost tracker content
        self.create_wattage_tracker_frame(bottom_frame)
        # Create the notification shortcut content
       

    def create_line_graph_frame(self, parent):
        """Create a frame to hold line graphs."""
        # Create a frame for the line graph
        graph_frame = customtkinter.CTkFrame(parent, width=880, height=461, fg_color='white', border_width=1, border_color='#b2b2b2', corner_radius=20)
        graph_frame.pack(side='left', anchor='nw', expand=False, padx=(30,0), pady=(15,0))
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
    
    def calculate_accumulated_wattage(self):
        """Calculate the accumulated wattage based on running appliances."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time  # Time in seconds
        self.start_time = current_time

        # Calculate the wattage consumed in the elapsed time
        for appliance in self.appliances:
            if appliance.state == 'ON':
                self.accumulated_wattage += (appliance.wattage / 3600) * elapsed_time  # Convert wattage to watt-hours
        # Update daily wattage
        current_day = datetime.now().day - 1  
        self.daily_wattage[current_day] += self.accumulated_wattage

        # Update monthly wattage
        current_month = datetime.now().month - 1  # Get the current month (0-indexed)
        self.monthly_wattage[current_month] += self.accumulated_wattage

        return self.accumulated_wattage
    
    def calculate_total_wattage(self):
        """Calculate the total wattage based on running appliances."""
        total_wattage = 0
        current_time = time.time()
        elapsed_time = current_time - self.start_time  # Time in seconds

        # Calculate the total wattage of running appliances
        for appliance in self.appliances:
            if appliance.state == 'ON':
                total_wattage += (appliance.wattage / 3600) * elapsed_time  # Sum up the wattage of all running appliances

        return total_wattage

    def update_total_wattage(self):
        """Update the total wattage every second."""
        if not self.winfo_exists():
            return  # Exit if the window has been destroyed

        current_time = datetime.now()
        self.x_data.append(current_time)
        self.y_data.append(self.calculate_total_wattage())

        self.after(1000, self.update_total_wattage)  # Update every second

    def create_line_graph(self, parent):
        """Create a real-time wattage line graph."""
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(padx=2, pady=2)

        self.ax.set_ylabel("Power (W)") 
        self.ax.legend(["Wattage"], loc="upper right")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.line, = self.ax.plot(self.x_data, self.y_data, label="Wattage", color="orange", linewidth=2)

        self.update_line_graph()

    def update_line_graph(self):
        """Update the line graph with new data."""
        if not self.winfo_exists():
            return  # Exit if the window has been destroyed

        current_time = datetime.now()
        self.x_data.append(current_time)
        self.y_data.append(self.calculate_total_wattage())

        self.line.set_data(self.x_data, self.y_data)

        # Make the y-axis dynamic
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()

        self.after(1000, self.update_line_graph)  # Update every second
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

    def store_monthly_wattage(self):
        """Store the accumulated wattage for the previous month."""
        current_month = datetime.now().month
        previous_month = current_month - 1 if current_month > 1 else 12
        
        # Store the accumulated wattage for the previous month
        self.monthly_historical_data = self.monthly_historical_data if hasattr(self, 'monthly_historical_data') else {}
        self.monthly_historical_data[previous_month] = self.accumulated_wattage
        
        # Reset accumulated wattage for the new month
        self.accumulated_wattage = 0

    def create_bar_graph_for_month(self, parent):
        """Create a bar graph showing current and previous month's wattage."""
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        
        # Prepare data for plotting
        x = list(range(1, 32))
        y = self.daily_wattage
        
        # Add historical data if available
        if hasattr(self, 'monthly_historical_data'):
            previous_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
            if previous_month in self.monthly_historical_data:
                previous_month_data = self.monthly_historical_data[previous_month]
                # Add visual comparison with previous month
                plt.axhline(y=previous_month_data, color='r', linestyle='--', label='Previous Month')

        # Create matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x, y, label='Current Month')

        # Set labels and title
        ax.set_xlabel('Day of the Month')
        ax.set_ylabel('Accumulated Wattage (Wh)')
        ax.set_title(f'Daily Accumulated Wattage for {current_month} {current_year}')
        ax.tick_params(labelsize=8)
        ax.legend()

        # Display the graph
        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.get_tk_widget().pack(padx=2, pady=2)

   
    def store_yearly_wattage(self):
        """Store the accumulated wattage for the previous year."""
        current_year = datetime.now().year
        self.yearly_historical_data = self.yearly_historical_data if hasattr(self, 'yearly_historical_data') else {}
        self.yearly_historical_data[current_year - 1] = sum(self.monthly_wattage)
        
        # Reset monthly wattage for the new year
        self.monthly_wattage = [0] * 12

    def create_bar_graph_for_year(self, parent):
        """Create a bar graph showing current and previous year's wattage."""
        current_year = datetime.now().year
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Prepare data for plotting
        x = list(range(1, 13))
        y = self.monthly_wattage
        
        # Add historical data if available
        if hasattr(self, 'yearly_historical_data') and (current_year - 1) in self.yearly_historical_data:
            previous_year_data = self.yearly_historical_data[current_year - 1]
            plt.axhline(y=previous_year_data/12, color='r', linestyle='--', 
                    label=f'Previous Year Monthly Average ({previous_year_data/12:.2f} kWh)')

        # Create matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ax.bar(x, y, label='Current Year')
        
        # Set labels and title
        ax.set_xlabel('Month')
        ax.set_ylabel('Accumulated Wattage (Wh)')
        ax.set_title(f'Monthly Accumulated Wattage for {current_year}')
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45)
        ax.tick_params(labelsize=8)
        ax.legend()

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom')

        # Display the graph
        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.get_tk_widget().pack(padx=2, pady=2)

    def create_appliance_controls_frame(self, parent):
        """Create controls for managing appliances."""
        # Create a frame for appliance controls
        self.appliance_control_frame = customtkinter.CTkFrame(parent, width=300, height=461, fg_color='white', border_width=1, border_color='#b2b2b2', corner_radius=20)
        self.appliance_control_frame.pack(side='top', anchor='ne', expand=False, padx=20, pady=(15,0))
        self.appliance_control_frame.pack_propagate(False)

        self.create_appliance_controls_content(self.appliance_control_frame)

    def count_running_appliances(self):
        """Count the number of appliances that are currently ON."""
        count = sum(1 for appliance in self.appliances if appliance.state == 'ON')
        print(count)
        return count

    def create_appliance_controls_content(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        appliance_running_count = self.count_running_appliances()
        print(f"Appliance running count: {appliance_running_count}")  # Debugging output

        # Example controls for appliances
        appliance_label = customtkinter.CTkLabel(parent, text="Running Appliances", font=('Arial', 16, 'bold'), corner_radius=20, text_color='black')
        appliance_label.pack(padx=10, pady=(15, 0), anchor='nw')

        if appliance_running_count > 0:
            print("Appliance running count is greater than 0")  # Debugging output
            # Create a scrollable frame inside the appliance control frame
            scrollable_frame = customtkinter.CTkScrollableFrame(parent, width=280, height=440, fg_color='#e0e0e0')
            scrollable_frame.pack(expand=True, fill='both', padx=10, pady=10)

            # Add a frame and power button for each running appliance
            for appliance in self.appliances:
                if appliance.state == 'ON':
                    print(f"Adding appliance to scrollable frame: {appliance.name}")  # Debugging output
                    appliance_frame = customtkinter.CTkFrame(scrollable_frame, fg_color="white", corner_radius=10, border_width=1, border_color="#b2b2b2")
                    appliance_frame.pack(fill='x', padx=5, pady=5)

                    name_label = customtkinter.CTkLabel(appliance_frame, text=appliance.name, font=('Arial', 14, 'bold'), text_color="black")
                    name_label.pack(side='left', padx=10, pady=5)

                    power_btn = customtkinter.CTkButton(
                        appliance_frame,
                        text="Turn Off",
                        width=70,
                        command=lambda a=appliance: self.toggle_appliance(a)
                    )
                    power_btn.pack(side='right', padx=10)
        else:
            no_appliance_frame = customtkinter.CTkFrame(parent, width=200, height=440, fg_color='#e0e0e0', corner_radius=20)
            no_appliance_frame.pack(expand=True, fill='both', padx=10, pady=10)

            no_appliances_label = customtkinter.CTkLabel(no_appliance_frame, text="No appliances running", font=('Arial', 16, 'bold'), text_color='#6a6a6a')
            no_appliances_label.pack(expand=True, fill='y', anchor='center', pady=(20, 5), padx=(10, 0))

    def create_goal_tracker_frame(self, parent):
        """Create the goal tracker frame."""
        self.tracker_frame = customtkinter.CTkFrame(parent, width=500, height=180, corner_radius=20, fg_color='white', border_width=1, border_color='#b2b2b2')
        self.tracker_frame.pack(side='left', anchor='center', expand=True, fill='none', padx=15, pady=(0,15))
        self.tracker_frame.pack_propagate(True)

        # Configure grid weights if needed
        self.create_goal_tracker_content(self.tracker_frame)

        # Debugging: Print the actual size after layout
        self.after(100, lambda: print("Goal Tracker Frame Size:", self.tracker_frame.winfo_width(), self.tracker_frame.winfo_height()))
    
    def start_monthly_cost_tracking(self):
        """Start tracking accumulated cost even without a goal."""
        if not self.winfo_exists():
            return

        accumulated_wattage = self.calculate_accumulated_wattage()
        self.monthly_accumulated_cost = self.convert_wattage_to_cost(accumulated_wattage)
        
        # Check for month change
        current_month = datetime.now().month
        if not hasattr(self, 'last_update_month'):
            self.last_update_month = current_month
        elif self.last_update_month != current_month:
            self.monthly_accumulated_cost = 0
            self.last_update_month = current_month

        self.after(1000, self.start_monthly_cost_tracking)
        self.check_goal_notifications()

    def create_goal_tracker_content(self, frame):
        """Create content for the goal tracker frame."""
        self.monthly_goal = None  # Initialize goal as None
        self.monthly_accumulated_cost = 0  # Initialize accumulated cost
        # Create a label for the goal tracker
        
        goal_tracker_label = customtkinter.CTkLabel(frame,
            text="Monthly Goal Tracker",
            font=('Arial', 14, 'bold'),
            wraplength=250,
            justify='center',
            text_color="black"
        )
        goal_tracker_label.pack(padx=50, pady=(5,0), anchor='center')


        if self.monthly_goal is None:
            # Show set goal button when no goal is set
            set_goal_button = customtkinter.CTkButton(
                frame,
                text="Set Monthly Goal",
                font=('Arial', 14, 'bold'),
                command=self.show_goal_dialog
            )
            set_goal_button.pack(padx=50, anchor='center', pady=(0,5), ipadx=10, ipady=10)
        else:
            self.tracker_slash_label = customtkinter.CTkLabel(frame,
                text=f"{self.monthly_accumulated_cost:.2f} / {self.monthly_goal:.2f} PHP",
                font=('Arial', 14, 'bold'),
                wraplength=200,
                justify='center',
                text_color='#8e8e8e',
                foreground_color='red'
            )
            self.tracker_slash_label.pack(padx=1000, anchor='center', pady=(0,15), ipadx=10, ipady=10)
            self.update_goal_progress()

    def show_goal_dialog(self):
        """Show dialog for setting monthly goal."""
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Set Monthly Goal")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()

        label = customtkinter.CTkLabel(dialog, text="Enter your target monthly cost (PHP):")
        label.pack(pady=20)

        entry = customtkinter.CTkEntry(dialog)
        entry.pack(pady=10)

        def save_goal():
            try:
                self.monthly_goal = float(entry.get())
                if hasattr(self, 'set_goal_button'):
                    self.set_goal_button.destroy()
                dialog.destroy()
                self.refresh_goal_tracker()
            except ValueError:
                error_label = customtkinter.CTkLabel(dialog, text="Please enter a valid number", text_color="red")
                error_label.pack(pady=5)

        save_button = customtkinter.CTkButton(dialog, text="Save", command=save_goal)
        save_button.pack(pady=20)

    def update_goal_progress(self):
        """Update the goal progress display."""
        if not self.winfo_exists():
            return

        current_month = datetime.now().month
        if not hasattr(self, 'last_update_month'):
            self.last_update_month = current_month
        elif self.last_update_month != current_month:
            # Reset accumulated cost at the start of new month
            self.monthly_accumulated_cost = 0
            self.last_update_month = current_month

        # Calculate and store the accumulated cost
        accumulated_wattage = self.calculate_accumulated_wattage()
        self.monthly_accumulated_cost = self.convert_wattage_to_cost(accumulated_wattage)
        
        # Format values for display
        formatted_cost = self.format_cost(self.monthly_accumulated_cost)
        formatted_goal = self.format_cost(self.monthly_goal)
        
        # Update display
        if hasattr(self, 'tracker_slash_label'):
            self.tracker_slash_label.configure(text=f"{formatted_cost} / {formatted_goal} PHP")

        self.after(1000, self.update_goal_progress)

    def convert_wattage_to_cost(self, wattage):
        """Accumulated wattage to cost in Philippine Peso."""
        cost_per_watt = 0.0024  # 1 Watt = 0.0024 Pesos
        return wattage * cost_per_watt


    def format_cost(self, value):
        """Format cost value with dynamic units"""
        if value >= 1000:
            return f"{value/1000:.2f}k"
        return f"{value:.2f}"

    def refresh_goal_tracker(self):
        """Refresh the goal tracker display."""
        # Clear all widgets in the frame
        for widget in self.tracker_frame.winfo_children():
            widget.destroy()

        goal_tracker_label = customtkinter.CTkLabel(self.tracker_frame,
            text="Monthly Goal Tracker",
            font=('Arial', 14, 'bold'),
            wraplength=250,
            justify='center',
            text_color="black"
        )
        goal_tracker_label.grid(row=0, column=1, padx=(0,15), pady=(5,0), sticky='sew', ipadx=50, ipady=10)

        self.tracker_slash_label = customtkinter.CTkLabel(self.tracker_frame,
            text=f"P {self.monthly_accumulated_cost:.2f} / {self.monthly_goal:.2f} PHP",
            font=('Arial', 16, 'bold'),
            wraplength=200,
            justify='center',
            text_color='#8e8e8e'
        )
        self.tracker_slash_label.grid(row=1, column=1, padx=(0,15), sticky='new', ipadx=50)
        self.update_goal_progress()

    def create_wattage_tracker_frame(self, parent):
        """Create the wattage tracker frame."""
        wattage_frame = customtkinter.CTkFrame(parent, width=500, height=180, corner_radius=20, fg_color='white', border_width=1, border_color='#b2b2b2')
        wattage_frame.pack(side='left', anchor='center', expand=True, fill='none', padx=15, pady=(0,15))
        wattage_frame.pack_propagate(True)

        self.create_wattage_tracker_content(wattage_frame)

        # Debugging: Print the actual size after layout
        self.after(100, lambda: print("Wattage Tracker Frame Size:", wattage_frame.winfo_width(), wattage_frame.winfo_height()))

    def create_wattage_tracker_content(self, frame):
        """Create content for the wattage tracker frame."""
        wattage_tracker_label = customtkinter.CTkLabel(frame,
            text="Monthly Wattage Tracker",
            font=('Arial', 14, 'bold'),
            wraplength=250,
            justify='center',
            text_color="black"
        )
        wattage_tracker_label.pack(padx=50, pady=(5,0), anchor='center')

        self.wattage_value_label = customtkinter.CTkLabel(frame,
            text="Accumulated Wattage: 0 kWh",
            font=('Arial', 16, 'bold'),
            wraplength=200,
            justify='center',
            text_color='#8e8e8e'
        )
        self.wattage_value_label.pack(padx=50, anchor='center', pady=(0,15))
        self.update_accumulated_wattage_display()


    def update_accumulated_wattage_display(self):
        """Update the accumulated wattage label every second."""
        if not self.winfo_exists():
            return

        accumulated_wattage = self.calculate_accumulated_wattage()
        unit = "kWh" if accumulated_wattage >= 1000 else "Wh"
        display_value = accumulated_wattage / 1000 if accumulated_wattage >= 1000 else accumulated_wattage
        
        self.wattage_value_label.configure(text=f"Accumulated Wattage: {display_value:.2f} {unit}")
        self.after(1000, self.update_accumulated_wattage_display)


#APPLIANCE PAGE ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def create_appliance_content(self, frame):
        """Create content for the Appliance tab."""
        appliance_label = customtkinter.CTkLabel(frame, text="APPLIANCES", text_color='black', font=('Helvetica', 24))
        appliance_label.pack(padx=30, pady=(15,0), anchor='nw')

        top_frame2 = customtkinter.CTkFrame(frame, fg_color="transparent")
        top_frame2.pack(side='top', anchor='center', padx=30, pady=(15, 0), fill='both', expand=True)

        self.create_appliance_manager_widget(top_frame2)

    def create_appliance_manager_widget(self, parent):
        """Create main card container"""
        appliance_card = customtkinter.CTkFrame(
            parent, 
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color='#b2b2b2'
        )
        appliance_card.pack(fill='both', expand=True, padx=30, pady=15)

        """Create content frame inside card - houses the  control panel and appliance list"""
        content_frame = customtkinter.CTkFrame(appliance_card, fg_color='transparent')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        """Create control panel - contains add and search frame, sorting and filtering"""
        control_frame = customtkinter.CTkFrame(content_frame, fg_color='transparent')
        control_frame.pack(fill='x', padx=10, pady=5)

        # Add Appliance Button
        add_btn = customtkinter.CTkButton(
            control_frame, 
            text="Add Appliance", 
            command=self.add_appliance_dialog, 
            height=40
        )
        add_btn.pack(side='left', padx=(0,5))

        # Search Frame
        search_frame = customtkinter.CTkFrame(control_frame, fg_color='transparent')
        search_frame.pack(side='left', padx=5)
        
        # Search Text Box
        search_entry = customtkinter.CTkEntry(
            search_frame, 
            placeholder_text="Search appliances...", 
            height=40, 
            width=400,
            fg_color='#e5e5e5',
            border_width=0,
            text_color='black'
        )
        search_entry.pack(side='left', padx=5)
        
        # Search button
        search_btn = customtkinter.CTkButton(search_frame, text="Search", height=40, command=lambda: self.search_appliances(search_entry.get()))
        search_btn.pack(side='left')
        
        # Sort button
        sort_options = ["Wattage", "State (On/Off)", "Alphabetical"]
        sort_var = customtkinter.StringVar(value="Sort by...")
        sort_menu = customtkinter.CTkOptionMenu(
            control_frame, 
            values=sort_options, 
            variable=sort_var, 
            height=40,
            command=self.sort_appliances
        )
        sort_menu.pack(side='right', padx=0)

        # Appliance list - scrollable frame
        self.list_frame = customtkinter.CTkScrollableFrame(content_frame, fg_color='#6a6a6a')
        self.list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.refresh_appliance_list()

    def add_appliance_dialog(self):
        """Open a dialog to add a new appliance."""
        # Create a dialog window for adding appliances
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Add Appliance")
        dialog.geometry("400x300")

        dialog.transient(self)
        dialog.focus_set()
        dialog.grab_set()
        dialog.lift()

        # Name Entry
        name_label = customtkinter.CTkLabel(dialog, text="Appliance Name:")
        name_label.pack(pady=5)
        name_entry = customtkinter.CTkEntry(dialog)
        name_entry.pack(pady=5)

        # Wattage Frame
        wattage_frame = customtkinter.CTkFrame(dialog)
        wattage_frame.pack(pady=10)
        
        # Wattage textbox
        wattage_entry = customtkinter.CTkEntry(wattage_frame, placeholder_text="Wattage")
        wattage_entry.pack(side='left', padx=5)

        units = ["W", "kW"]
        unit_var = customtkinter.StringVar(value="W")
        unit_menu = customtkinter.CTkOptionMenu(wattage_frame, values=units, variable=unit_var)
        unit_menu.pack(side='left')

        def save_appliance():
            appliance_name = name_entry.get()
            wattage = float(wattage_entry.get())
            unit = unit_var.get()
            schedule_start = None
            schedule_end = None

            if appliance_name and wattage:
                # Create an Appliance object
                new_appliance = Appliance(appliance_name, wattage, unit, schedule_start, schedule_end)
                
                # Add to appliance list
                self.appliances.append(new_appliance)
                
                new_appliance.save_to_file("appliances.txt")

                # Refresh the appliance list display
                self.refresh_appliance_list()
                
                # Close dialog
                dialog.destroy()

        # Save Button
        save_btn = customtkinter.CTkButton(dialog, text="Save Appliance", command=save_appliance)
        save_btn.pack(pady=20)

    def search_appliances(self, search_term):
        """Search appliances by name"""
        # Clear existing items in list frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Filter appliances based on search term
        filtered_appliances = [
            appliance for appliance in self.appliances 
            if search_term.lower() in appliance.name.lower()
        ]

        # Display filtered appliances
        for appliance in filtered_appliances:
            item_frame = customtkinter.CTkFrame(
                self.list_frame,
                fg_color="white",
                corner_radius=10,
                border_width=1,
                border_color="#b2b2b2"
            )
            item_frame.pack(fill='x', padx=10, pady=5)

            # Appliance name and detail
            name_label = customtkinter.CTkLabel(
                item_frame, 
                text=f"{appliance.name} - {appliance.display_wattage()}{appliance.unit}", 
                font=('Arial', 14, 'bold'),
                text_color="black"
            )
            name_label.pack(side='left', padx=15, pady=10)

            # Control buttons frame
            btn_frame = customtkinter.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.pack(side='right', padx=10)

            # Power button
            power_btn = customtkinter.CTkButton(
                btn_frame,
                text=appliance.state,
                width=70,
                command=lambda a=appliance: self.toggle_appliance(a)
            )
            power_btn.pack(side='right', padx=5)
            self.appliance_buttons[appliance.name] = power_btn

            # Edit button
            edit_btn = customtkinter.CTkButton(
                btn_frame,
                text="Edit",
                width=70,
                command=lambda a=appliance: self.edit_appliance(a)
            )
            edit_btn.pack(side='right', padx=5)

            # Delete button
            delete_btn = customtkinter.CTkButton(
                btn_frame,
                text="Delete",
                width=70,
                command=lambda a=appliance: self.delete_appliance(a)
            )
            delete_btn.pack(side='right', padx=5)

   
    def refresh_appliance_list(self):
        """Refresh the appliance list display"""
        # Clear existing items
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Create item frame for each appliance
        for appliance in self.appliances:
            item_frame = customtkinter.CTkFrame(
                self.list_frame,
                fg_color="white",
                corner_radius=10,
                border_width=1,
                border_color="#b2b2b2"
            )
            item_frame.pack(fill='x', padx=10, pady=5)

            # Appliance name and detail
            name_label = customtkinter.CTkLabel(
                item_frame, 
                text=f"{appliance.name} - {appliance.display_wattage()}{appliance.unit}", 
                font=('Arial', 14, 'bold'),
                text_color="black"
            )
            name_label.pack(side='left', padx=15, pady=10)

            # Control buttons frame
            btn_frame = customtkinter.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.pack(side='right', padx=10)

            # Schedule button
            schedule_btn = customtkinter.CTkButton(
                btn_frame,
                text="Schedule",
                width=70,
                command=lambda a=appliance: self.create_schedule_dialog(a)
            )
            schedule_btn.pack(side='right', padx=5)
            # Power button
            power_btn = customtkinter.CTkButton(
                btn_frame,
                text=appliance.state,
                width=70,
                command=lambda a=appliance: self.toggle_appliance(a)
            )
            power_btn.pack(side='right', padx=5) 
            self.appliance_buttons[appliance.name] = power_btn  # Store button reference (toggle On and Off)

            # Edit button
            edit_btn = customtkinter.CTkButton(
                btn_frame,
                text="Edit",
                width=70,
                command=lambda a=appliance: self.edit_appliance(a)
            )
            edit_btn.pack(side='right', padx=5)

            # Delete button
            delete_btn = customtkinter.CTkButton(
                btn_frame,
                text="Delete",
                width=70,
                command=lambda a=appliance: self.delete_appliance(a)
            )
            delete_btn.pack(side='right', padx=5)
    
    def sort_appliances(self, criterion):
        """Sort appliances based on the selected criterion."""
        if criterion == "Wattage":
            self.appliances.sort(key=lambda a: a.wattage, reverse=True)
        elif criterion == "State (On/Off)":
            self.appliances.sort(key=lambda a: a.state, reverse=True)
        elif criterion == "Alphabetical":
            self.appliances.sort(key=lambda a: a.name.lower())

        # Refresh the appliance list to reflect the new order
        self.refresh_appliance_list()

    def toggle_appliance(self, appliance):
        appliance.state = 'ON' if appliance.state == 'OFF' else 'OFF'
        if appliance.name in self.appliance_buttons:
            self.appliance_buttons[appliance.name].configure(text=appliance.state)
        running_count = self.count_running_appliances()
        print(f"Total running appliances: {running_count}")
        self.create_appliance_controls_content(self.appliance_control_frame)
        self.update_idletasks()
    
    def delete_appliance(self, appliance):
        """Open a confirmation dialog to delete the selected appliance."""
        # Create a dialog window for confirmation
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Confirm Deletion")
        dialog.geometry("300x150")

        dialog.transient(self)
        dialog.focus_set()
        dialog.grab_set()
        dialog.lift()

        # Confirmation message
        message_label = customtkinter.CTkLabel(dialog, text=f"Are you sure you want to delete '{appliance.name}'?", wraplength=250, justify='center')
        message_label.pack(pady=20)

        # Button frame
        button_frame = customtkinter.CTkFrame(dialog, fg_color='transparent')
        button_frame.pack(pady=10)

        def confirm_delete():
            # Remove the appliance from the list
            if appliance in self.appliances:
                self.appliances.remove(appliance)
                self.refresh_appliance_list()
                self.create_appliance_controls_content(self.appliance_control_frame)
                self.update_appliance_file()
            dialog.destroy()

        def cancel_delete():
            dialog.destroy()

        # Confirm button
        confirm_btn = customtkinter.CTkButton(button_frame, text="Yes", command=confirm_delete)
        confirm_btn.pack(side='left', padx=10)

        # Cancel button
        cancel_btn = customtkinter.CTkButton(button_frame, text="No", command=cancel_delete)
        cancel_btn.pack(side='right', padx=10)

    def edit_appliance(self, appliance):
        """Open a dialog to edit the selected appliance."""
        # Create a dialog window for editing appliances
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Edit Appliance")
        dialog.geometry("400x300")

        dialog.transient(self)
        dialog.focus_set()
        dialog.grab_set()
        dialog.lift()

        # Name Entry
        name_label = customtkinter.CTkLabel(dialog, text="Appliance Name:")
        name_label.pack(pady=5)
        name_entry = customtkinter.CTkEntry(dialog)
        name_entry.insert(0, appliance.name)
        name_entry.pack(pady=5)

        # Wattage Frame
        wattage_frame = customtkinter.CTkFrame(dialog)
        wattage_frame.pack(pady=10)
        
        # Wattage textbox
        wattage_entry = customtkinter.CTkEntry(wattage_frame, placeholder_text="Wattage")
        wattage_entry.insert(0, str(appliance.wattage))
        wattage_entry.pack(side='left', padx=5)

        units = ["W", "kW"]
        unit_var = customtkinter.StringVar(value=appliance.unit)
        unit_menu = customtkinter.CTkOptionMenu(wattage_frame, values=units, variable=unit_var)
        unit_menu.pack(side='left')

        def save_changes():
            appliance.name = name_entry.get()
            new_wattage = float(wattage_entry.get())
            new_unit = unit_var.get()

            if new_unit == "kW":
                appliance.wattage = new_wattage * 1000
            else:
                appliance.wattage = new_wattage

            appliance.unit = unit_var.get()
            self.refresh_appliance_list()
            self.create_appliance_controls_content(self.appliance_control_frame)
            # Update the appliance file
            self.update_appliance_file()
            dialog.destroy()

        # Save Button
        save_btn = customtkinter.CTkButton(dialog, text="Save Changes", command=save_changes)
        save_btn.pack(pady=20)

    def update_appliance_file(self):
        """Update the appliance file with the current list of appliances."""
        with open("appliances.txt", 'w') as file:
            for appliance in self.appliances:
                file.write(f"{appliance.name},{appliance.wattage},{appliance.unit},{appliance.schedule_start},{appliance.schedule_end},{appliance.state}\n")
    def create_schedule_dialog(self, appliance):
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Schedule {appliance.name}")
        dialog.geometry("300x300")

        dialog.transient(self)
        dialog.focus_set()
        dialog.grab_set()
        dialog.lift()
  
        schedule_frame = customtkinter.CTkFrame(dialog)
        schedule_frame.pack(pady=20)
        
        start_label = customtkinter.CTkLabel(schedule_frame, text="Start Time (HH:MM)")
        start_label.pack()
        start_time = customtkinter.CTkEntry(schedule_frame, placeholder_text="08:00", text_color='black')
        start_time.pack(pady=5)
        
        end_label = customtkinter.CTkLabel(schedule_frame, text="End Time (HH:MM)")
        end_label.pack()
        end_time = customtkinter.CTkEntry(schedule_frame, placeholder_text="17:00", text_color='black')
        end_time.pack(pady=5)
        
        def save_schedule():
            appliance.schedule_start = start_time.get()
            appliance.schedule_end = end_time.get()
            self.start_schedule_checker()
            dialog.destroy()
    
        save_btn = customtkinter.CTkButton(dialog, text="Save Schedule", command=save_schedule)
        save_btn.pack(pady=20)

    def start_schedule_checker(self):
        def check_schedules():
            current_time = datetime.now().time()
            
            for appliance in self.appliances:
                if appliance.schedule_start and appliance.schedule_end:  # Check if schedule exists
                    print(f"Checking appliance: {appliance.name}")
                    print(f"Schedule Start: {appliance.schedule_start}, Schedule End: {appliance.schedule_end}")
                    start_time = datetime.strptime(appliance.schedule_start, "%H:%M").time()
                    end_time = datetime.strptime(appliance.schedule_end, "%H:%M").time()
                    if start_time <= current_time <= end_time:
                        if appliance.state != 'ON':
                            appliance.state = 'ON'
                            if appliance.name in self.appliance_buttons:
                                self.appliance_buttons[appliance.name].configure(text='ON')
                            self.refresh_appliance_list()
                            self.create_appliance_controls_content(self.appliance_control_frame)
                    else:
                        if appliance.state != 'OFF':
                            appliance.state = 'OFF'
                            if appliance.name in self.appliance_buttons:
                                self.appliance_buttons[appliance.name].configure(text='OFF')
                            self.refresh_appliance_list()
                            self.create_appliance_controls_content(self.appliance_control_frame)
            
            self.after(60000, check_schedules)  # Check every minute
        
        check_schedules()


    def clear_schedule(self, appliance):
        appliance.schedule_start = None
        appliance.schedule_end = None
        
#NOTIFICATION PAGE ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def create_notification_tab(self, frame):
        """Create content for the Notification tab."""
        self.notifications_list = []
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
        
        self.notifications_2frame = customtkinter.CTkScrollableFrame(notifications_frame, fg_color="white", width=760, height=540, corner_radius=15)
        self.notifications_2frame.grid(row=1, column=0, columnspan=4, padx=15, pady=(25,15), sticky='nsew')
        self.check_goal_notifications()

    def check_goal_notifications(self):
        """Create notifications based on goal progress"""
        if self.monthly_goal is not None:
            percentage = (self.monthly_accumulated_cost / self.monthly_goal) * 100
            
            for widget in self.notifications_2frame.winfo_children():
                widget.destroy()
                
            # Create card-style notification
            def create_notification_card(message, urgency_color):
                card = customtkinter.CTkFrame(
                    self.notifications_2frame,
                    fg_color="white",
                    corner_radius=10,
                    border_width=2,
                    border_color=urgency_color
                )
                card.pack(fill='x', padx=10, pady=5)
                
                notification = customtkinter.CTkLabel(
                    card,
                    text=message,
                    text_color='black',
                    font=('Helvetica', 12),
                    wraplength=600
                )
                notification.pack(pady=10, padx=10)
                
            if percentage >= 100:
                create_notification_card(
                    "⚠️ Alert: Monthly goal exceeded! Current usage: {:.2f} PHP".format(self.monthly_accumulated_cost),
                    "#ff0000"  # Red for exceeded
                )
            elif percentage >= 75:
                create_notification_card(
                    "⚠️ Warning: Approaching monthly goal! Usage at 75%",
                    "#ffa500"  # Orange for warning
                )
            elif percentage >= 50:
                create_notification_card(
                    "ℹ️ Notice: Usage reached 50% of monthly goal",
                    "#ffff00"  # Yellow for notice
                )

            # Update notifications every minute
            self.after(60000, self.check_goal_notifications)


#SETTINGS PAGE -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_settings_tab(self, frame):
        settings_label = customtkinter.CTkLabel(frame, text="SETTINGS", text_color='black', font=('Helvetica', 24))
        settings_label.pack(padx=20, pady=(15, 0), anchor='nw')

        """Create main card container"""
        settings_card = customtkinter.CTkFrame(
            frame,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color='#b2b2b2'
        )

        settings_card.pack(fill='both', expand=True, padx=30, pady=15)

        """Create content frame inside card - houses the control panel and appliance list"""
        content_frame = customtkinter.CTkFrame(settings_card, fg_color='transparent')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Create a frame to hold the inner frame and the buttons (for centering)
        parent_frame = customtkinter.CTkFrame(
            content_frame,
            fg_color='transparent',
            width=600,  # Set the width of the parent frame
            height=400,  # Set the height of the parent frame
        )
        parent_frame.pack(side='top', anchor='center', expand=True)  # Center the parent frame in content_frame

        # Create a frame to hold the buttons on the right side
        button_frame = customtkinter.CTkFrame(
            parent_frame,
            fg_color='transparent',  # Make the frame background invisible
            width=200,
            height=400  # Height to space out the buttons
        )
        button_frame.pack(side='right', anchor='center', padx=10, pady=10)  # Position buttons on the right

        # Add rectangle buttons stacked on top of each other in the button frame
        change_password_button = customtkinter.CTkButton(
            button_frame,
            text="Change Password",
            width=200,
            height=50,
            corner_radius=10
        )
        change_password_button.pack(pady=(10, 5))  # Spacing between buttons

        # Function to show custom dialog
        def show_privacy_policy_custom():
            # Create a new top-level window
            dialog = customtkinter.CTkToplevel()
            dialog.title("Privacy Policy")
            dialog.geometry("400x200")  # Set the size of the dialog
            dialog.transient(self)
            dialog.focus_set()
            dialog.grab_set()
            dialog.lift()
            
            # Add a label to the dialog
            label = customtkinter.CTkLabel(dialog, text="Here is the Privacy Policy details...", font=("Helvetica", 16))
            label.pack(padx=20, pady=20)

            # Add a button to close the dialog
            close_button = customtkinter.CTkButton(dialog, text="Close", command=dialog.destroy)
            close_button.pack(pady=10)

        # Privacy Policy button with custom dialog
        privacy_policy_button = customtkinter.CTkButton(
            button_frame,
            text="Privacy Policy",
            width=200,
            height=50,
            corner_radius=10,
            command=show_privacy_policy_custom  # Show the custom dialog when clicked
        )
        privacy_policy_button.pack(pady=5)

        # Function to show custom Contact Us dialog
        def show_contact_us():
            # Create a new top-level window
            dialog = customtkinter.CTkToplevel()
            dialog.title("Contact Us")
            dialog.geometry("400x300")  # Set the size of the dialog
            dialog.transient(self)
            dialog.focus_set()
            dialog.grab_set()
            dialog.lift()
            
            # Add a label to the dialog
            label = customtkinter.CTkLabel(dialog, text="If you have any questions, feel free to contact us.", font=("Helvetica", 14))
            label.pack(padx=20, pady=10)
            
            # Add a Textbox for contact message
            message_label = customtkinter.CTkLabel(dialog, text="Your Message:", font=("Helvetica", 12))
            message_label.pack(padx=20, pady=10, anchor="w")
            
            message_entry = customtkinter.CTkEntry(dialog, width=300)
            message_entry.pack(padx=20, pady=5)
            
            # Add a Send button
            send_button = customtkinter.CTkButton(dialog, text="Send Message", command=dialog.destroy)
            send_button.pack(pady=10)
            
            # Add a Close button
            close_button = customtkinter.CTkButton(dialog, text="Close", command=dialog.destroy)
            close_button.pack(pady=5)

        # Contact Us button with custom dialog
        contact_us_button = customtkinter.CTkButton(
            button_frame,
            text="Contact Us",
            width=200,
            height=50,
            corner_radius=10,
            command=show_contact_us  # Show the custom dialog when clicked
        )
        contact_us_button.pack(pady=5)

        # Function to show custom User Management dialog
        def show_user_management():
            # Create a new top-level window
            dialog = customtkinter.CTkToplevel()
            dialog.title("User Management")
            dialog.geometry("400x400")  # Set the size of the dialog
            dialog.transient(self)
            dialog.focus_set()
            dialog.grab_set()
            dialog.lift()
            
            # Add a label to the dialog
            label = customtkinter.CTkLabel(dialog, text="Manage your users here.", font=("Helvetica", 14))
            label.pack(padx=20, pady=10)
            
            # Add a Textbox for user name
            user_label = customtkinter.CTkLabel(dialog, text="Username:", font=("Helvetica", 12))
            user_label.pack(padx=20, pady=10, anchor="w")
            
            user_entry = customtkinter.CTkEntry(dialog, width=300)
            user_entry.pack(padx=20, pady=5)
            
            # Add a Textbox for email
            email_label = customtkinter.CTkLabel(dialog, text="Email address:", font=("Helvetica", 12))
            email_label.pack(padx=20, pady=10, anchor="w")
            
            email_entry = customtkinter.CTkEntry(dialog, width=300)
            email_entry.pack(padx=20, pady=5)

            # Add a Textbox for contact
            contact_label = customtkinter.CTkLabel(dialog, text="Contact number:", font=("Helvetica", 12))
            contact_label.pack(padx=20, pady=10, anchor="w")
            
            contact_entry = customtkinter.CTkEntry(dialog, width=300)
            contact_entry.pack(padx=20, pady=5)
            
            # Add a Save button
            save_button = customtkinter.CTkButton(dialog, text="Save User", command=dialog.destroy)
            save_button.pack(pady=10)
            
            # Add a Close button
            close_button = customtkinter.CTkButton(dialog, text="Close", command=dialog.destroy)
            close_button.pack(pady=5)

        # User Management button with custom dialog
        user_management_button = customtkinter.CTkButton(
            button_frame,
            text="User Management",
            width=200,
            height=50,
            corner_radius=10,
            command=show_user_management  # Show the custom dialog when clicked
        )
        user_management_button.pack(pady=5)

        """Create smaller inner frame within the content frame"""
        inner_frame = customtkinter.CTkFrame(
            parent_frame,
            fg_color="#d9d9d9",  # Light gray background for visibility
            width=250,           # Width smaller than the content_frame
            height=300,          # Height smaller than the content_frame
            corner_radius=15
        )
        inner_frame.pack(side='left', anchor='center', padx=10, pady=10)  # Align to the left of the parent frame
        inner_frame.pack_propagate(False)

        # Add labels and text box inside the inner frame
        name = customtkinter.CTkLabel(inner_frame, text="Name:", text_color='black', font=('Helvetica', 16))
        name.pack(padx=10, pady=(10, 5), anchor='nw')

        email = customtkinter.CTkLabel(inner_frame, text="Email address:", text_color='black', font=('Helvetica', 16))
        email.pack(padx=10, pady=(5, 10), anchor='nw')

        contact = customtkinter.CTkLabel(inner_frame, text="Contact address:", text_color='black', font=('Helvetica', 16))
        contact.pack(padx=10, pady=(5, 10), anchor='nw')
        

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

    def logout(self):
        self.destroy()  # Close the current window
        subprocess.run(["python", "Final_Product.py"])

if __name__ == "__main__":
    app = App()
    app.mainloop()