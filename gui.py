import tkinter as tk
from tkinter import messagebox
from auth import login, register, get_current_user, clear_session
from file_transfer import send_file, receive_file
from history import view_history  # ✅ Ensure this is correctly imported

# Initialize GUI
root = tk.Tk()
root.title("Secure File Transfer Tool")
root.geometry("500x400")
root.configure(bg="#282C34")

# Function to refresh dashboard
def refresh_dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    current_user = get_current_user()

    tk.Label(root, text="📌 Dashboard", font=("Arial", 16), bg="#282C34", fg="white").pack(pady=10)

    if current_user:
        tk.Label(root, text=f"👤 Logged in as: {current_user}", font=("Arial", 12), bg="#282C34", fg="lightgreen").pack()
    else:
        tk.Label(root, text="❌ Not logged in!", font=("Arial", 12), bg="#282C34", fg="red").pack()

    tk.Button(root, text="📤 Send File", command=send_file, font=("Arial", 12), bg="#61AFEF", width=25).pack(pady=5)
    tk.Button(root, text="📥 Receive File", command=receive_file, font=("Arial", 12), bg="#E06C75", width=25).pack(pady=5)
    tk.Button(root, text="📜 View History", command=view_history, font=("Arial", 12), bg="#98C379", width=25).pack(pady=5)
    tk.Button(root, text="🔄 Refresh", command=refresh_dashboard, font=("Arial", 12), bg="#98C379", width=25).pack(pady=5)
    tk.Button(root, text="❌ Logout", command=logout, font=("Arial", 12), bg="#D19A66", width=25).pack(pady=5)

# Function to handle logout
def logout():
    clear_session()  # Clears session file
    messagebox.showinfo("Logout", "✅ Successfully logged out!")  
    start_home()  # Redirect to login/register screen

# Function to start home page (Login/Register)
def start_home():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="🔒 Secure File Transfer", font=("Arial", 16), bg="#282C34", fg="white").pack(pady=20)
    tk.Button(root, text="🔑 Login", command=lambda: login(refresh_dashboard), font=("Arial", 12), bg="#61AFEF", width=25).pack(pady=5)
    tk.Button(root, text="🆕 Register", command=lambda: register(refresh_dashboard), font=("Arial", 12), bg="#98C379", width=25).pack(pady=5)

    if get_current_user():
        refresh_dashboard()

start_home()
root.mainloop()