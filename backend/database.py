import sqlite3
from pathlib import Path

#  The database is one file, saved next to this code
DB_PATH = Path(__file__).parent / "preppilot.db"

def get_connection():
    # Open the database-> Rows can be read by column name, like row["email"]
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Create the users table if it does not exist yet
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

    #  One profile per user. user_id is the primary key, so a user can't have two.
    # skills is a list saved as text, like '["HTML", "AWS"]'
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id     INTEGER PRIMARY KEY,
            target_role TEXT NOT NULL,
            study_year  INTEGER NOT NULL,
            skills      TEXT NOT NULL DEFAULT '[]',
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


# Runs only when you start this file directly(python database.py)
if __name__  == "__main__":
    init_db()
    print("Database ready")