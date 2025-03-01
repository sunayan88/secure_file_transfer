Python File Transfer Tool
==========================

This tool allows you to transfer files over a local network using Python and Tkinter.
It enables easy file sharing between computers within the same network.

Features:
---------
- Simple and fast file transfer
- Graphical user interface (GUI) built with Tkinter
- Uses IP addresses for transferring files between computers on the same network

Requirements:
-------------
- Python 3.x (https://www.python.org/downloads/)
- Tkinter (usually pre-installed with Python)

Setup Instructions:
-------------------
1. Download or clone the repository:
   - Clone via Git: 
     git clone https://github.com/yourusername/file-transfer-tool.git
   - Or download the ZIP and extract it.

2. Install required Python packages:
   Tkinter is included with Python, but if needed, you can install it using:
   pip install tkinter

3. Run the tool:
   - Open a terminal or command prompt in the directory containing `file_transfer.py`.
   - Run the script with the command:
     python file_transfer.py

Usage Instructions:
-------------------
1. **Sending Files**:
   - Open the tool on the sender's computer.
   - Enter the receiver’s IP address (make sure both systems are on the same network).
   - Click "Select File" to choose the file you want to send.
   - Click "Send" to start the transfer.

2. **Receiving Files**:
   - Open the tool on the receiver's computer.
   - The file will be automatically saved in the designated folder once the transfer is completed.

Troubleshooting:
----------------
- Both computers must be on the same local network.
- Ensure no firewall or antivirus is blocking the connection.
- Verify the IP address by running `ipconfig` (Windows) or `ifconfig` (Linux/Mac).

License:
--------
This project is licensed under the MIT License.

For support or questions, contact [Your Contact Information].
