import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("TESTING ZONE")
        self.geometry("1080x720")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create a frame for the vertical tabs
        self.tab_frame = customtkinter.CTkFrame(self, width=200)
        self.tab_frame.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="ns")
        self.tab_frame.grid_rowconfigure(0, weight=1)  # Top spacer
        self.tab_frame.grid_rowconfigure(1, weight=0)  # Tab 1
        self.tab_frame.grid_rowconfigure(2, weight=0)  # Tab 2
        self.tab_frame.grid_rowconfigure(3, weight=0)  # Tab 3
        self.tab_frame.grid_rowconfigure(4, weight=0)  # Tab 4
        self.tab_frame.grid_rowconfigure(5, weight=1)  # Middle spacer
        self.tab_frame.grid_rowconfigure(6, weight=0)  # Bottom Tab
        self.tab_frame.grid_rowconfigure(7, weight=1)  # Bottom spacer
        
        # Create a frame for the tab content
        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create tab buttons
        self.tab_buttons = []
        self.create_tab_button("Tab 1", 1)
        self.create_tab_button("Tab 2", 2)
        self.create_tab_button("Tab 3", 3)
        self.create_tab_button("Tab 4", 4)
        self.create_tab_button("Bottom Tab", 6)
        
        # Create tab content
        self.tab_contents = []
        self.create_tab_content("Content for Tab 1", 0, line_graph=True)
        self.create_tab_content("Content for Tab 2", 1)
        self.create_tab_content("Content for Tab 3", 2)
        self.create_tab_content("Content for Tab 4", 3)
        self.create_tab_content("Content for Bottom Tab", 4)
        
        # Show the first tab by default
        self.show_tab(0)
    
    def create_tab_button(self, text, row):
        button = customtkinter.CTkButton(self.tab_frame, text=text, command=lambda: self.show_tab(row - 1))
        button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        self.tab_buttons.append(button)
    
    def create_tab_content(self, text, index, line_graph=False):
        frame = customtkinter.CTkFrame(self.content_frame)
        if line_graph:
            self.create_line_graph_frame(frame)
        else:
            label = customtkinter.CTkLabel(frame, text=text)
            label.pack(padx=20, pady=20)
        self.tab_contents.append(frame)
    
    def create_line_graph_frame(self, parent):
        # Create a sub-frame for the graph
        graph_frame = customtkinter.CTkFrame(parent)
        graph_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create the line graph inside the sub-frame
        self.create_line_graph(graph_frame)
    
    def create_line_graph(self, parent):
        # Sample data for the line graph
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 4, 9, 16, 25]
        
        # Create a figure and axis
        fig, ax = plt.subplots()
        ax.plot(x, y, marker='o')
        
        # Set labels and title
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_title('Sample Line Graph')
        
        # Create a canvas and add the figure to it
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # Close the figure to prevent it from being updated outside the main thread
        plt.close(fig)
    
    def show_tab(self, index):
        for i, frame in enumerate(self.tab_contents):
            if i == index:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()
        # Update the event loop to ensure proper rendering
        self.update_idletasks()

if __name__ == "__main__":
    app = App()
    app.mainloop()