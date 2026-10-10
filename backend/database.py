import sqlite3
from pathlib import Path

#  The database is one file, saved next to this code
DB_PATH = Path(__file__).parent / "preppilot.db"

def get_connection():
    # Open the database-> Rows can be read by column name, like row["email"]
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory =sqlite3.Row
    return conn

def init_db():
    # Create the users table if it does not exists yet
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name           TEXT NOT NULL,
            email               TEXT NOT NULL UNIQUE,
            password_hash       TEXT NOT NULL,
            created_at          TEXT DEFAULT CURRENT_TIMESTAMP
        )

    """)
    conn.commit()
    conn.close()


# Runs only when you start this file directly(python database.py)
if __name__  == "__main__":
    init_db()
    print("Database ready")