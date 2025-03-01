import mysql.connector
import socket
import os
import bcrypt
import argparse
import threading
import sys
import re  # Added for sanitizing filenames

PORT = 5001
BUFFER_SIZE = 4096
TIMEOUT = 60  # Auto-exit timeout for receiving files

# Connect to MySQL
db = mysql.connector.connect(host="localhost", user="root", password="", database="file_sharing")
cursor = db.cursor()

current_user = None  # Track logged-in user
stop_event = threading.Event()  # Event to stop receiving

# Function to sanitize filenames
def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*#]', "", filename)

def get_current_user():
    return current_user

def login(username, password):
    """ Logs in a user via CLI arguments """
    global current_user
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        current_user = username
        print(f"✅ Successfully logged in as {username}!")
    else:
        print("❌ Invalid credentials! Try again.")

def register(username, password):
    """ Registers a new user via CLI arguments """
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        db.commit()
        print(f"✅ Registration successful for {username}! You can now login.")
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")

def send_file():
    """ Guides user to send a file via CLI """
    sender = get_current_user()
    if not sender:
        print("❌ You must be logged in to send files!")
        return

    receiver_ip = input("📡 Enter receiver's IP address: ").strip()
    file_path = input("📁 Enter the full path of the file to send: ").strip()

    if not os.path.exists(file_path):
        print("❌ File not found! Make sure the path is correct.")
        return

    try:
        s = socket.socket()
        s.connect((receiver_ip, PORT))
        s.send(f"{sender}|{os.path.basename(file_path)}".encode())

        with open(file_path, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                s.send(chunk)

        s.send(b"EOF")
        print(f"✅ File '{file_path}' sent successfully to {receiver_ip}!")
    except Exception as e:
        print(f"❌ Error sending file: {e}")
    finally:
        s.close()

def wait_for_enter():
    """ Stops the receiving process when Enter is pressed """
    sys.stdin.read(1)  # Instantly detect Enter press
    if not stop_event.is_set():
        print("\n❌ File receiving canceled by user. Returning to menu...")
        stop_event.set()  # Stop receiving process

def receive_file():
    """ Receives incoming files with proper EOF handling and stability """
    print("📡 Waiting for incoming files... (Press Enter to cancel)")

    stop_event.clear()  # Reset stop event before starting

    # Start a thread to listen for Enter key
    input_thread = threading.Thread(target=wait_for_enter, daemon=True)
    input_thread.start()

    s = socket.socket()
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    s.settimeout(1)  # 🔥 Lower timeout to check every second instead of freezing

    try:
        while not stop_event.is_set():  # Stop if user cancels
            try:
                conn, addr = s.accept()
                print(f"✅ Connected to {addr}")

                data = conn.recv(BUFFER_SIZE).decode()

                # 🛠 Fix: Validate the received data format
                if "|" not in data:
                    print("❌ File reception failed: Corrupted data received!")
                    conn.close()
                    return

                parts = data.split("|")

                if len(parts) != 2:
                    print("❌ File reception failed: Invalid data format received!")
                    conn.close()
                    return

                sender = parts[0]
                filename = sanitize_filename(parts[1])  # Sanitize the filename

                if not filename:
                    print("❌ Invalid filename received!")
                    conn.close()
                    return

                # 🔥 FIX: Ensure file saves correctly (default to current directory)
                save_path = input("📂 Enter directory to save the file (or press Enter for current directory): ").strip()
                if not save_path:
                    save_path = os.getcwd()  # Default to current directory

                save_path = os.path.normpath(save_path)  # Normalize the path

                if not os.path.exists(save_path):
                    print("❌ Invalid folder path! Transfer canceled.")
                    conn.close()
                    return
                
                file_path = os.path.join(save_path, filename)

                print(f"💾 Saving file to: {file_path}")

                with open(file_path, "wb") as f:
                    while True:
                        data = conn.recv(BUFFER_SIZE)
                        if data.endswith(b"EOF"):
                            f.write(data[:-3])  # 🔥 FIX: Remove EOF marker before writing!
                            break
                        f.write(data)

                conn.close()
                print(f"✅ File received successfully at: {file_path}")
                return  # Exit after receiving a file

            except socket.timeout:
                continue  # 🔥 Instead of waiting full timeout, check stop_event every second

    except KeyboardInterrupt:
        print("\n❌ Process interrupted. Returning to menu...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        s.close()
        stop_event.set()  # Ensure exit
        return  # Ensure function exits properly

def logout():
    """ Logs out the user """
    global current_user
    current_user = None
    print("✅ Logged out successfully!")

def interactive_menu():
    """ Shows interactive CLI menu for users """
    while True:
        print("\n🔒 Secure File Transfer CLI")
        print("1️⃣ Login")
        print("2️⃣ Register")
        print("3️⃣ Send File")
        print("4️⃣ Receive File")
        print("5️⃣ Logout")
        print("6️⃣ Exit")

        choice = input("\n💡 Select an option (1-6): ").strip()

        if choice == "1":
            username = input("👤 Enter username: ").strip()
            password = input("🔑 Enter password: ").strip()
            login(username, password)
        elif choice == "2":
            username = input("👤 Enter new username: ").strip()
            password = input("🔒 Enter new password: ").strip()
            register(username, password)
        elif choice == "3":
            send_file()
        elif choice == "4":
            receive_file()
        elif choice == "5":
            logout()
        elif choice == "6":
            print("👋 Exiting Secure File Transfer CLI...")
            break
        else:
            print("❌ Invalid choice! Please enter a number from 1 to 6.")

def main():
    """ Command-line argument parser with guided mode """
    parser = argparse.ArgumentParser(description="Secure File Transfer CLI")
    parser.add_argument("--receive", action="store_true", help="Receive an incoming file")
    args = parser.parse_args()

    if args.receive:
        receive_file()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()