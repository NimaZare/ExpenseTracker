import os
import sqlite3
from tools.utils import Utils
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()
DATABASE_NAME = os.getenv("DATABASE_NAME", "expenses.db")
DB_URL = Utils.resource_path(f"data/{DATABASE_NAME}")

db_directory = os.path.dirname(DB_URL)
if not os.path.exists(db_directory):
    os.makedirs(db_directory, exist_ok=True)


@contextmanager
def get_db_connection(timeout: float = 30.0):
    """
    Get a synchronous database connection using a standard context manager.
    """
    conn = sqlite3.connect(DB_URL, timeout=timeout) 
    try:
        conn.execute("PRAGMA journal_mode = WAL") 
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        
        conn.row_factory = sqlite3.Row 
        yield conn
    finally:
        conn.close() 


def setup_database():
    """Create tables and set WAL mode."""
    with get_db_connection() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        );
        CREATE TABLE IF NOT EXISTS preferences (
            item TEXT PRIMARY KEY,
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            category TEXT,
            account TEXT NOT NULL,
            description TEXT,
            is_active INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        ''')
        
        db.commit()

