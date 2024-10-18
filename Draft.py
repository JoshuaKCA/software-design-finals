import customtkinter
from register import Register  # Import the Register class

root = customtkinter.CTk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # configure window
        self.geometry("1080x720")
        self._max_height = (screen_height)
        self._max_width = (screen_width)
        self.title("Draft")
        
        # set grid
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 8, 9, 10), weight=1)
        self.grid_rowconfigure((3, 4, 5, 6, 7), weight=0)
        
        # Initialize widget references
        self.user = None
        self.password = None
        self.login = None
        self.register = None
        self.icon = None
        self.toplevel_window = None
        
        # Call the function to add initial widgets
        self.create_login_widgets()

    def create_login_widgets(self):
        # Destroy existing widgets if they exist
        self.destroy_widgets()
        
        # Widgets for Login
        self.user = customtkinter.CTkEntry(self, placeholder_text="username", justify="center")
        self.user.grid(row=3, column=1, padx=100, pady=2, sticky="ew")
        
        self.password = customtkinter.CTkEntry(self, placeholder_text="password", justify="center", show="*")
        self.password.grid(row=4, column=1, padx=100, pady=2, sticky="ew")
        
        self.login = customtkinter.CTkButton(self, command=self.login_click, text="Login")
        self.login.grid(row=5, column=1, padx=200, pady=5, sticky="ew")
        
        self.register = customtkinter.CTkButton(self, command=self.register_click, text="Register")
        self.register.grid(row=6, column=1, padx=200, pady=5, sticky="ew")

    def create_register_widgets(self):
        # Destroy existing widgets if they exist
        self.destroy_widgets()
        
        # Create an instance of the Register class and add its widgets to the main window
        self.register_form = Register(self)
        self.register_form.grid(row=0, column=0, sticky="nsew")

    def destroy_widgets(self):
        # Destroy existing widgets if they exist
        if self.user:
            self.user.destroy()
        if self.password:
            self.password.destroy()
        if self.login:
            self.login.destroy()
        if self.register:
            self.register.destroy()
        if self.icon:
            self.icon.destroy()
        if hasattr(self, 'register_form'):
            self.register_form.destroy()
        
    def open_toplevel(self, message):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = customtkinter.CTkToplevel(self)  # create window if its None or destroyed
            self.toplevel_window.title("Invalid Input")
            self.toplevel_window.geometry("300x150")
            label = customtkinter.CTkLabel(self.toplevel_window, text=message)
            label.pack(pady=20)
            button = customtkinter.CTkButton(self.toplevel_window, text="OK", command=self.toplevel_window.destroy)
            button.pack(pady=10)
            self.toplevel_window.lift()  # Bring the window to the front
            self.toplevel_window.focus_force()  # Force focus on the window
        else:
            self.toplevel_window.focus()  # if window exists focus it
            
    # Button click event for login
    def login_click(self):
        # Get the username and password from the entry widgets
        username = self.user.get()
        password = self.password.get()
        
        # Check if either field is empty
        if not username or not password:
            self.open_toplevel("Error: Username and password cannot be empty.")
            return
        
        # Check if the username and password are in the users.txt file
        try:
            with open("users.txt", "r") as file:
                for line in file:
                    user, pw = line.strip().split(",")
                    if user == username and pw == password:
                        print("Login successful")
                        self.create_new_gui()
                        return
            self.open_toplevel("Login failed")
        except FileNotFoundError:
            self.open_toplevel("No users registered yet.")
        
    # Button click event for register
    def register_click(self):
        # Switch to the registration form
        self.create_register_widgets()

    def create_new_gui(self):
        # Destroy current widgets
        self.destroy_widgets()
        
        # Create new widgets for the new GUI
        self.new_label = customtkinter.CTkLabel(self, text="Welcome to the new GUI!")
        self.new_label.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
        
        self.new_button = customtkinter.CTkButton(self, text="New Button", command=self.new_button_click)
        self.new_button.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

    def new_button_click(self):
        print("New button click")

if __name__ == "__main__":
    app = App()
    app.mainloop()