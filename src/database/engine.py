import os
import aiosqlite
from tools.utils import Utils
from dotenv import load_dotenv
from contextlib import asynccontextmanager


load_dotenv()
DATABASE_NAME = os.getenv("DATABASE_NAME", "expenses.db")
DB_URL = Utils.resource_path(f"data/{DATABASE_NAME}")

db_directory = os.path.dirname(DB_URL)
if not os.path.exists(db_directory):
    os.makedirs(db_directory, exist_ok=True)


@asynccontextmanager
async def get_db_connection(timeout: float = 30.0):
    """
    Get an asynchronous database connection using async context manager.
    """
    conn = await aiosqlite.connect(DB_URL, timeout=timeout)
    try:
        await conn.execute("PRAGMA journal_mode = WAL")
        await conn.execute("PRAGMA synchronous = NORMAL")
        await conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = aiosqlite.Row
        yield conn
    finally:
        await conn.close()


async def setup_database():
    """Create tables and set WAL mode."""
    async with get_db_connection() as db:
        await db.executescript('''
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
