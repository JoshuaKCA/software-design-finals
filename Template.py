import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import make_interp_spline
import random
from datetime import datetime
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

    def display_wattage(self):
        if self.unit == "kW":
            display_value = self.wattage / 1000
        else:
            display_value = self.wattage
        return f"{display_value}"



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry("1600x900")
        self.title("SEMS")
        
        self.title("Insert Window title")
        self.state('zoomed')

        """Appliance List"""
        self.appliances = [] 
        self.appliance_buttons = {}
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
        tab_names = ["Dashboard", "WIP", "Appliance", "Notifications", "Settings"]
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
        elif index == 2:  # Appliance Page
            self.create_appliance_content(frame)
        elif index == 3: # Notification Page
            self.create_notification_tab(frame)
        elif index == 4: # Settings Page
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
        # Create the notification shortcut content
        self.create_notification_shortcut_frame(bottom_frame)

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
            dialog.destroy()

        # Save Button
        save_btn = customtkinter.CTkButton(dialog, text="Save Changes", command=save_changes)
        save_btn.pack(pady=20)

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
        
    
#SETTINGS PAGE -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_settings_tab(self, frame):

        settings_label = customtkinter.CTkLabel(frame, text="Settings", font=("Arial", 18, "bold"))
        settings_label.pack(pady=20)

        # Create a frame for settings content
        settings_frame = customtkinter.CTkFrame(frame, fg_color="#f0f0f0", corner_radius=10)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Energy-saving mode toggle
        self.energy_mode_var = customtkinter.StringVar(value="Off")
        energy_mode_label = customtkinter.CTkLabel(settings_frame, text="Energy-saving Mode:")
        energy_mode_label.pack(pady=5)
        energy_mode_toggle = customtkinter.CTkSwitch(settings_frame, text="Enable", variable=self.energy_mode_var, onvalue="On", offvalue="Off")
        energy_mode_toggle.pack(pady=5)

        # Additional settings widgets can be added here
        # Example: Add a slider for brightness control
        brightness_label = customtkinter.CTkLabel(settings_frame, text="Brightness:")
        brightness_label.pack(pady=5)
        brightness_slider = customtkinter.CTkSlider(settings_frame, from_=0, to=100)
        brightness_slider.pack(pady=5)
    
    
    # Logout function
    def logout(self):
        self.destroy()  # Close the current window
        subprocess.run(["python", "Final_Product.py"])

if __name__ == "__main__":
    app = App()
    app.mainloop()