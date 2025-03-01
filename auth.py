import mysql.connector
import bcrypt
import tkinter as tk
from tkinter import messagebox

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="file_sharing"
)
cursor = db.cursor()

SESSION_FILE = "session.txt"

# Function to get the currently logged-in user
def get_current_user():
    try:
        with open(SESSION_FILE, "r") as f:
            return f.read().strip() or None
    except FileNotFoundError:
        return None

# Function to store logged-in user
def set_current_user(username):
    with open(SESSION_FILE, "w") as f:
        f.write(username)

# Function to clear session (Logout)
def clear_session():
    open(SESSION_FILE, "w").close()

# Function to login an existing user
def login(refresh_callback):
    login_window = tk.Toplevel()
    login_window.title("Login")

    tk.Label(login_window, text="Username:").pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    tk.Label(login_window, text="Password:").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    def authenticate_user():
        username = username_entry.get()
        password = password_entry.get()

        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
            set_current_user(username)  # Store session
            messagebox.showinfo("Success", f"✅ Welcome, {username}!")
            login_window.destroy()
            refresh_callback()  # Refresh dashboard
        else:
            messagebox.showerror("Error", "❌ Invalid username or password!")

    tk.Button(login_window, text="Login", command=authenticate_user).pack()
    login_window.mainloop()

# Function to register a new user
def register(refresh_callback):
    register_window = tk.Toplevel()
    register_window.title("Register")

    tk.Label(register_window, text="Username:").pack()
    username_entry = tk.Entry(register_window)
    username_entry.pack()

    tk.Label(register_window, text="Password:").pack()
    password_entry = tk.Entry(register_window, show="*")
    password_entry.pack()

    def register_user():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password cannot be empty!")
            return

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
            db.commit()
            messagebox.showinfo("Success", "✅ Registration successful! Please log in.")
            register_window.destroy()
            refresh_callback()  # Redirect to dashboard after registering
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    tk.Button(register_window, text="Register", command=register_user).pack()
    register_window.mainloop()