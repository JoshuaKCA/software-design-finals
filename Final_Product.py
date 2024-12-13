import customtkinter
import subprocess

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
        self.message_label = None
        
        # Call the function to add initial widgets
        self.create_login_widgets()

    def create_login_widgets(self):
        # Destroy existing widgets if they exist
        self.destroy_widgets()
        
        # Widgets for Login
        self.user = customtkinter.CTkEntry(self, placeholder_text="username", justify="center", height=30, width=100)
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
        
        self.username = customtkinter.CTkEntry(self, placeholder_text="username", justify="center")
        self.username.grid(row=3, column=1, padx=100, pady=2, sticky="ew")
        
        self.password = customtkinter.CTkEntry(self, placeholder_text="password", justify="center", show="*")
        self.password.grid(row=4, column=1, padx=100, pady=2, sticky="ew")
        
        self.verify_password = customtkinter.CTkEntry(self, placeholder_text="verify password", justify="center", show="*")
        self.verify_password.grid(row=5, column=1, padx=100, pady=2, sticky="ew")
        
        self.email = customtkinter.CTkEntry(self, placeholder_text="email", justify="center")
        self.email.grid(row=6, column=1, padx=100, pady=2, sticky="ew")
        
        self.number = customtkinter.CTkEntry(self, placeholder_text="number", justify="center")
        self.number.grid(row=7, column=1, padx=100, pady=2, sticky="ew")
        
        self.register_button = customtkinter.CTkButton(self, text="Register", command=self.register_user)
        self.register_button.grid(row=8, column=1, padx=200, pady=5, sticky="ew")
        
        self.back_to_login = customtkinter.CTkButton(self, text="Back to Login", command=self.create_login_widgets)
        self.back_to_login.grid(row=9, column=1, padx=200, pady=5, sticky="ew")
        
    def register_user(self):
        username = self.username.get()
        password = self.password.get()
        verify_password = self.verify_password.get()
        email = self.email.get()
        number = self.number.get()
        
        if not username or not password or not verify_password or not email or not number:
            self.show_message("Error: All fields are required.")
            return
        
        if password != verify_password:
            self.show_message("Error: Passwords do not match.")
            return
        
        # Save user input to two local files
        with open("users.txt", "a") as file1, open("user_details.txt", "a") as file2:
            file1.write(f"{username},{password}\n")
            file2.write(f"{username},{email},{number}\n")
        
        self.show_message("User registered successfully")
        self.create_login_widgets()

    def destroy_widgets(self):
        if self.user:
            self.user.destroy()
        if self.password:
            self.password.destroy()
        if self.login:
            self.login.destroy()
        if self.register:
            self.register.destroy()
        if self.message_label:
            self.message_label.destroy()
        if hasattr(self, 'username'):
            self.username.destroy()
        if hasattr(self, 'verify_password'):
            self.verify_password.destroy()
        if hasattr(self, 'email'):
            self.email.destroy()
        if hasattr(self, 'number'):
            self.number.destroy()
        if hasattr(self, 'register_button'):
            self.register_button.destroy()
        if hasattr(self, 'back_to_login'):
            self.back_to_login.destroy()

    def login_click(self):
        username = self.user.get()
        password = self.password.get()
        
        if self.check_credentials(username, password):
            self.destroy()
            subprocess.run(["python", "template.py"])
        else:
            self.message_label = customtkinter.CTkLabel(self, text="Invalid username or password")
            self.message_label.grid(row=7, column=1, padx=100, pady=2, sticky="ew")

    def check_credentials(self, username, password):
        try:
            with open("users.txt", "r") as file:
                for line in file:
                    stored_username, stored_password = line.strip().split(",")
                    if username == stored_username and password == stored_password:
                        return True
        except FileNotFoundError:
            self.message_label = customtkinter.CTkLabel(self, text="User file not found")
            self.message_label.grid(row=7, column=1, padx=100, pady=2, sticky="ew")
        return False

    def register_click(self):
        self.create_register_widgets()

    def show_message(self, message):
        if self.message_label:
            self.message_label.destroy()
        self.message_label = customtkinter.CTkLabel(self, text=message)
        self.message_label.grid(row=10, column=1, padx=200, pady=5, sticky="ew")

if __name__ == "__main__":
    root = customtkinter.CTk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("green")
    
    app = App()
    app.mainloop()