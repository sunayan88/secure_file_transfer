import mysql.connector
from tkinter import messagebox
from auth import get_current_user  # Import the function from auth.py

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="file_sharing"
)
cursor = db.cursor()

def view_history():
    """ Displays file transfer history """
    current_user = get_current_user()  # Now this function is defined
    if not current_user:
        messagebox.showerror("Error", "❌ You must be logged in to view history!")
        return

    cursor.execute("SELECT * FROM file_transfers WHERE sender = %s OR receiver = %s", (current_user, current_user))
    transfers = cursor.fetchall()

    if not transfers:
        messagebox.showinfo("History", "No file transfers found!")
        return

    history_text = "📜 File Transfer History:\n\n"
    for transfer in transfers:
        history_text += f"📄 File: {transfer[3]}\n"
        history_text += f"👤 Sender: {transfer[1]}\n"
        history_text += f"👥 Receiver: {transfer[2]}\n"
        history_text += f"📅 Timestamp: {transfer[4]}\n\n"

    messagebox.showinfo("History", history_text)