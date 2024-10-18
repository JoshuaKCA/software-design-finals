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
        self.tab_frame.grid_rowconfigure(0, weight=1)
        
        # Create a frame for the tab content
        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create tab buttons
        self.tab_buttons = []
        self.create_tab_button("Tab 1", 0)
        self.create_tab_button("Tab 2", 1)
        self.create_tab_button("Tab 3", 2)
        
        # Create tab content
        self.tab_contents = []
        self.create_tab_content("Content for Tab 1", 0)
        self.create_tab_content("Content for Tab 2", 1)
        self.create_tab_content("Content for Tab 3", 2)
        
        # Show the first tab by default
        self.show_tab(0)
    
    def create_tab_button(self, text, index):
        button = customtkinter.CTkButton(self.tab_frame, text=text, command=lambda: self.show_tab(index))
        button.grid(row=index, column=0, padx=10, pady=10, sticky="ew")
        self.tab_buttons.append(button)
    
    def create_tab_content(self, text, index):
        frame = customtkinter.CTkFrame(self.content_frame)
        if index == 0:
            label = customtkinter.CTkLabel(frame, text=text)
            label.pack(padx=20, pady=20)
        elif index == 1:
            self.create_line_graph(frame)
        else:
            label = customtkinter.CTkLabel(frame, text=text)
            label.pack(padx=20, pady=20)
        self.tab_contents.append(frame)
    
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
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def show_tab(self, index):
        for i, frame in enumerate(self.tab_contents):
            if i == index:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

if __name__ == "__main__":
    app = App()
    app.mainloop()