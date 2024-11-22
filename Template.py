import customtkinter
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Insert Window title")
        self.geometry("1080x720")

        # Configure grid layout 
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create Header (header)
        self.header = customtkinter.CTkFrame(self, fg_color="#ffffff", height=65, corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(70, 0))
        self.header.grid_propagate(False)
        
        # Create Sidebar (sidebar)
        self.sidebar = customtkinter.CTkFrame(self, fg_color="black", width=70, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)  # This centers the buttons

        # Create Main Content Area (main_content)
        self.main_content = customtkinter.CTkFrame(self, fg_color="#f0f0f0", corner_radius=0)  # dirty white color
        self.main_content.grid(row=1, column=1, sticky="nsew")


    # Sidebar/Tab
        #Logo Icon
        # Load and create PNG image
        png_image = customtkinter.CTkImage(
            light_image=Image.open("svg_files\Lightbulb 02.png"),
            dark_image=Image.open("svg_files\Lightbulb 02.png"),
            size=(50, 50)  # Set your desired size
        )
        
        # Add image to sidebar
        self.image_label = customtkinter.CTkLabel(self.sidebar, image=png_image, text="")
        self.image_label.grid(row=0, column=0, pady=10)

        # Create Sidebar/Tab Buttons
        self.tab_buttons = []
        self.create_tab_button("1", 0)
        self.create_tab_button("2", 1)
        self.create_tab_button("3", 2)
        self.create_tab_button("4", 3)

    # Main Content
        # Create Tab Content
        self.tab_contents = []
        self.create_tab_content("Content for Tab 1", 0, line_graph=True)
        self.create_tab_content("Content for Tab 2", 1)
        self.create_tab_content("Content for Tab 3", 2)
        self.create_tab_content("Content for Tab 4", 3)

        # Show the first tab by default
        self.show_tab(0)

    # METHODS FOR WIDGETS
    #Create Tab Buttons for Sidebar for Navigation
    def create_tab_button(self, text, index):
        button = customtkinter.CTkButton(self.sidebar, text=text, command=lambda: self.show_tab(index), width=50, height=50)
        button.grid(row=index + 1, column=0, padx=10, pady=10, sticky="ew")
        self.tab_buttons.append(button)

    #Create Tab Contents
    def create_tab_content(self, text, index, line_graph=False):
        frame = customtkinter.CTkFrame(self.main_content)
        
        if index == 2:  # Tab 3
            self.create_appliance_manager(frame)
        elif line_graph:
            self.create_line_graph_frame(frame)
        else:
            label = customtkinter.CTkLabel(frame, text=text)
            label.pack(padx=20, pady=20)
        self.tab_contents.append(frame)

    def create_appliance_manager(self, parent):
        # Top control panel
        control_frame = customtkinter.CTkFrame(parent)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Add Appliance Button
        add_btn = customtkinter.CTkButton(control_frame, text="Add Appliance", command=self.add_appliance_dialog)
        add_btn.pack(side='left', padx=5)
        
        # Search Frame
        search_frame = customtkinter.CTkFrame(control_frame)
        search_frame.pack(side='left', padx=5)
        search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Search appliances...")
        search_entry.pack(side='left', padx=5)
        search_btn = customtkinter.CTkButton(search_frame, text="Search")
        search_btn.pack(side='left')
        
        # Sort Dropdown
        sort_options = ["Wattage", "State (On/Off)", "Alphabetical"]
        sort_var = customtkinter.StringVar(value="Sort by...")
        sort_menu = customtkinter.CTkOptionMenu(control_frame, values=sort_options, variable=sort_var)
        sort_menu.pack(side='right', padx=5)
        
        # Appliance List Frame
        list_frame = customtkinter.CTkScrollableFrame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

    def add_appliance_dialog(self):
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
        item_frame = customtkinter.CTkFrame(list_frame)
        item_frame.pack(fill='x', pady=2)
        
        # Appliance Name
        name_label = customtkinter.CTkLabel(item_frame, text=appliance_data['name'])
        name_label.pack(side='left', padx=5)
        
        # Control Buttons Frame
        btn_frame = customtkinter.CTkFrame(item_frame)
        btn_frame.pack(side='right')
        
        # Toggle Button
        toggle_btn = customtkinter.CTkButton(btn_frame, text="ON/OFF", width=70)
        toggle_btn.pack(side='right', padx=2)
        
        # Schedule Button
        schedule_btn = customtkinter.CTkButton(btn_frame, text="Schedule", width=70)
        schedule_btn.pack(side='right', padx=2)
        
        # Edit Button
        edit_btn = customtkinter.CTkButton(btn_frame, text="Edit", width=70)
        edit_btn.pack(side='right', padx=2)
        
        # Delete Button
        delete_btn = customtkinter.CTkButton(btn_frame, text="Delete", width=70)
        delete_btn.pack(side='right', padx=2)
    #Creates line bar graph frame or container to hold the graph
    def create_line_graph_frame(self, parent):
        # Create a sub-frame for the graph
        graph_frame = customtkinter.CTkFrame(parent, width=600, height=400)
        graph_frame.pack(side='left', anchor='n', expand=False, padx=20, pady=20)
        graph_frame.pack_propagate(False)  # Force frame to keep its size
    
        # Create button frame to hold buttons
        button_frame = customtkinter.CTkFrame(graph_frame, width=600, height=30)
        button_frame.pack(side='top', anchor='w', fill=None, padx=20, pady=5)
    
        # Create buttons for different graphs
        graph1_btn = customtkinter.CTkButton(button_frame, text="Day", command=lambda: self.switch_graph(0, graph_frame), width=100, height=30)
        graph1_btn.pack(side='left', padx=0)
    
        graph2_btn = customtkinter.CTkButton(button_frame, text="Month", command=lambda: self.switch_graph(1, graph_frame), width=100, height=30)
        graph2_btn.pack(side='left', padx=2)
    
        graph3_btn = customtkinter.CTkButton(button_frame, text="Year", command=lambda: self.switch_graph(2, graph_frame), width=100, height=30)
        graph3_btn.pack(side='left', padx=0)
    
        # Show first graph by default
        self.switch_graph(0, graph_frame)

    #Create line graph for Day (12:00 am - 11:59 pm)   
    def create_line_graph(self, parent):
        # Sample data for the line graph
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 4, 9, 16, 25]
        
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(7,4))
        #ax.___ is for specification of type of graph (ax.plot is for plot graph)
        ax.plot(x, y, marker='o')
        
        # Set labels and title
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_title('Sample Line Graph')
        ax.tick_params(labelsize=8)  # Smaller tick labels
        
        # Create a canvas and add the figure to it with minimal padding
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=2, pady=2)
    
        plt.tight_layout()

        # Close the figure to prevent it from being updated outside the main thread
        plt.close(fig) 
    
    #Allows you to switch between graphs
    def switch_graph(self, graph_index, parent):
        # Clear existing graph
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
        
        if graph_index == 0:
            self.create_line_graph(parent) #Day Graph (Line_plot)
        elif graph_index == 1:
            self.create_bar_graph_for_month(parent) #Month Graph (Bar_plot)
        elif graph_index == 2:
            self.create_bar_graph_for_year(parent) #Year Graph (Bar_plot)

    #Create a bar graph for the month
    def create_bar_graph_for_month(self, parent):
        #X-Value Month-Frame (Day 1 - 31)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
        y = [23, 45, 56, 78, 43, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        fig, ax = plt.subplots(figsize=(7,4))
        #ax.___ is for specification of type of graph (ax.bar is for bar graph)
        ax.bar(x, y)
        
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Sample Bar Graph')
        ax.tick_params(labelsize=8)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=2, pady=2)
        plt.tight_layout()
        plt.close(fig)

    #Create Bar Graph for Year
    def create_bar_graph_for_year(self, parent):
        #X-Value Year-Frame (January-December)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]   
        y = [2, 5, 3, 8, 6, 7, 1, 4, 9, 5, 0, 0]
            
        fig, ax = plt.subplots(figsize=(7,4))
        #ax.___ is for specification of type of graph (ax.bar is for bar graph)
        ax.bar(x, y)
        
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Sample Bar Graph')
        ax.tick_params(labelsize=8)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=2, pady=2)
        plt.tight_layout()
        plt.close(fig)
    
    #Shows Tab Content
    def show_tab(self, index):
        for i, frame in enumerate(self.tab_contents):
            if i == index:
                frame.grid(row=0, column=0, sticky="nsew", in_=self.main_content) #appends the widgets to main_content
            else:
                frame.grid_forget()

         # Configure main_content grid weights
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
    
        self.update_idletasks()

        # Update the event loop to ensure proper rendering
        self.update_idletasks()


        
if __name__ == "__main__":
    app = App()
    app.mainloop()
