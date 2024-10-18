import customtkinter

class Register(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 8, 9, 10), weight=1)
        self.grid_rowconfigure((3, 4, 5, 6, 7), weight=0)
        
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
        
        self.back_to_login = customtkinter.CTkButton(self, text="Back to Login", command=parent.create_login_widgets)
        self.back_to_login.grid(row=9, column=1, padx=200, pady=5, sticky="ew")
        
    def register_user(self):
        username = self.username.get()
        password = self.password.get()
        verify_password = self.verify_password.get()
        email = self.email.get()
        number = self.number.get()
        
        if not username or not password or not verify_password or not email or not number:
            self.open_toplevel("Error: All fields are required.")
            return
        
        if password != verify_password:
            self.open_toplevel("Error: Passwords do not match.")
            return
        
        # Save user input to two local files
        with open("users.txt", "a") as file1, open("user_details.txt", "a") as file2:
            file1.write(f"{username},{password}\n")
            file2.write(f"{username},{email},{number}\n")
        
        self.open_toplevel("User registered successfully")
        self.master.create_login_widgets()
        
    def open_toplevel(self, message):
        toplevel_window = customtkinter.CTkToplevel(self)
        toplevel_window.title("Message")
        toplevel_window.geometry("300x150")
        label = customtkinter.CTkLabel(toplevel_window, text=message)
        label.pack(pady=20)
        button = customtkinter.CTkButton(toplevel_window, text="OK", command=toplevel_window.destroy)
        button.pack(pady=10)
        toplevel_window.lift()
        toplevel_window.focus_force()