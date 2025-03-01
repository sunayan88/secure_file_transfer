import mysql.connector

# Connect to MySQL (XAMPP)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
)
cursor = db.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS file_sharing")
cursor.execute("USE file_sharing")

# Create Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
)
""")

# Create File Transfers Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_transfers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(50) NOT NULL,
    receiver VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("✅ Database and Tables Created Successfully.")

db.commit()
cursor.close()
db.close()