import sqlite3
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

def initialize_database():
    conn = sqlite3.connect('EnerCheck_Users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect('EnerCheck_Users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    finally:
        conn.close()

# Function to verify user login
def login_user(username, password):
    conn = sqlite3.connect('EnerCheck_Users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        messagebox.showinfo("Login Success", f"Welcome, {username}!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

# Initialize database
initialize_database()

class LoginSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login & Registration System")
        self.geometry("1080x720")

         # Toggle between login and registration
        self.mode = "login"  # Default mode is login

        # Frame for UI
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

# Title Label
        self.title_label = ctk.CTkLabel(self.frame, text="Login", font=("Arial", 20))
        self.title_label.pack(pady=10)

        # Username Entry
        self.username_label = ctk.CTkLabel(self.frame, text="Username:")
        self.username_label.pack(pady=5)

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="username", justify="center", width = 200, corner_radius=50)
        self.username_entry.pack(pady=5)

        # Password Entry
        self.password_label = ctk.CTkLabel(self.frame, text="Password:")
        self.password_label.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.frame, show="*", placeholder_text="password", justify="center", width = 200, corner_radius=50)
        self.password_entry.pack(pady=5)

        # Login/Register Button
        self.action_button = ctk.CTkButton(self.frame, text="Login", command=self.handle_action)
        self.action_button.pack(pady=10)

        # Toggle Mode Button
        self.toggle_button = ctk.CTkButton(self.frame, text="Switch to Register", command=self.toggle_mode)
        self.toggle_button.pack(pady=10)

    def toggle_mode(self):
        if self.mode == "login":
            self.mode = "register"
            self.title_label.configure(text="Register")
            self.action_button.configure(text="Register")
            self.toggle_button.configure(text="Switch to Login")
        else:
            self.mode = "login"
            self.title_label.configure(text="Login")
            self.action_button.configure(text="Login")
            self.toggle_button.configure(text="Switch to Register")

    def handle_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Warning", "Please fill out all fields.")
            return

        if self.mode == "login":
            login_user(username, password)
        elif self.mode == "register":
            register_user(username, password)


# Run the application
if __name__ == "__main__":
    app = LoginSystem()
    app.mainloop()
