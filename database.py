import sqlite3
import hashlib
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        # ✅ FIX: Store DB in Documents/TARKEEZ folder so it persists safely
        self.db_path = self.get_db_path()
        self.create_table()

    def get_db_path(self):
        """Returns the path to Documents/TARKEEZ/tarkeez_users.db"""
        # Get standard Documents folder
        base_dir = Path.home() / "Documents" / "TARKEEZ"
        base_dir.mkdir(parents=True, exist_ok=True) # Create folder if not exists
        return str(base_dir / "tarkeez_users.db")

    def create_table(self):
        """Creates the users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path) # Use full path
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hashes password for security (SHA-256)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, email, password):
        """Adds a new user. Returns True if successful, False if email exists."""
        if not email or not password:
            return False, "Email and Password cannot be empty."

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            hashed_pw = self.hash_password(password)
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_pw))
            conn.commit()
            return True, "Account created successfully! You can now login."
        except sqlite3.IntegrityError:
            return False, "This email is already registered."
        finally:
            conn.close()

    def authenticate_user(self, email, password):
        """Checks if email/password match."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        hashed_pw = self.hash_password(password)
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed_pw))
        user = cursor.fetchone()
        
        conn.close()
        return user is not None