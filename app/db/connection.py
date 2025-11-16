# app/db/connection.py
import sqlite3
from sqlite3 import Error

# create a database connection
def create_connection(db_file: str):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        print(f"✅ Connected to database: {db_file}")
        return conn
    except Error as e:
        print(f"❌ An error occurred while connecting to database: {e}")
        return None
