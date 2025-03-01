import socket
import os
import threading
import re
from tkinter import filedialog, messagebox, simpledialog
from auth import get_current_user  # ✅ Lazy import to prevent circular import issues

PORT = 5001
BUFFER_SIZE = 4096
receiving = False  # Prevent multiple receiver instances

# Function to sanitize filenames
def sanitize_filename(filename):
    """Removes invalid characters and trims whitespace/newlines from filenames."""
    filename = re.sub(r'[<>:"/\\|?*\n]', "", filename)  # Remove illegal characters
    filename = filename.strip()  # Remove trailing spaces or hidden characters
    return filename

# Function to send a file
def send_file():
    sender = get_current_user()
    if not sender:
        messagebox.showerror("Error", "❌ You must be logged in to send files!")
        return

    filename = filedialog.askopenfilename(title="Select File to Send")
    if not filename:
        return

    receiver_ip = simpledialog.askstring("Receiver", "Enter receiver's IP address:")
    if not receiver_ip:
        return

    note = simpledialog.askstring("Add Note", "Enter a note (optional):") or "No note"

    thread = threading.Thread(target=start_sending, args=(sender, filename, receiver_ip, note), daemon=True)
    thread.start()

def start_sending(sender, filename, receiver_ip, note):
    try:
        s = socket.socket()
        s.settimeout(10)
        s.connect((receiver_ip, PORT))
        sanitized_filename = sanitize_filename(os.path.basename(filename))

        # ✅ Send sender info, filename, and note (no hash or file size)
        s.send(f"{sender}|{sanitized_filename}|{note}".encode())

        response = s.recv(BUFFER_SIZE).decode()
        if response != "ACCEPT":
            messagebox.showwarning("Transfer Declined", "❌ Receiver declined the file transfer.")
            s.close()
            return

        with open(filename, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                s.send(chunk)

        s.send(b"EOF")  # ✅ Send EOF marker
        s.close()

        messagebox.showinfo("Success", "✅ File sent successfully!")

    except socket.timeout:
        messagebox.showerror("Error", "⏳ Connection timed out! The receiver may be offline.")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to send file: {str(e)}")

# Function to receive a file
def receive_file():
    global receiving
    if receiving:  
        messagebox.showwarning("Warning", "⚠ Already waiting for a file!")
        return

    receiving = True
    thread = threading.Thread(target=start_receiving, daemon=True)
    thread.start()

def start_receiving():
    global receiving
    receiver = get_current_user()
    if not receiver:
        messagebox.showerror("Error", "❌ You must be logged in to receive files!")
        receiving = False
        return

    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", PORT))
        s.listen(1)

        messagebox.showinfo("Listening", "📡 Waiting for incoming files...")

        conn, addr = s.accept()
        sender_info = conn.recv(BUFFER_SIZE).decode(errors="ignore")

        if "|" not in sender_info:
            conn.close()
            receiving = False
            return

        sender, filename, note = sender_info.split("|", 2)
        filename = sanitize_filename(filename)

        accept = messagebox.askyesno("Incoming File", f"📥 File: {filename}\n📨 From: {sender}\n📝 Note: {note}\n\nDo you want to accept?")
        if not accept:
            conn.send("DECLINE".encode())
            conn.close()
            receiving = False
            return

        conn.send("ACCEPT".encode())

        save_path = filedialog.askdirectory(title="Select Folder to Save File")
        if not save_path:
            messagebox.showwarning("Warning", "No folder selected! File transfer canceled.")
            conn.close()
            receiving = False
            return

        file_path = os.path.join(save_path, "received_" + filename)

        with open(file_path, "wb") as f:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if data.endswith(b"EOF"):  
                    f.write(data[:-3])  # ✅ Remove EOF before writing
                    break
                f.write(data)

        conn.close()
        receiving = False

        messagebox.showinfo("Success", f"✅ File received successfully!\nSaved to: {file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"❌ File reception failed: {str(e)}")
        receiving = False
