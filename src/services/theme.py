import sqlite3
from typing import Dict, Optional
from services.base import BaseService
from database.engine import get_db_connection


class ThemeService(BaseService):
    def __init__(self):
        super().__init__("preferences")

    def get_by_item(self, item: str) -> Optional[Dict]:
        """Fetches a preference by its unique item."""
        query = f"SELECT * FROM {self.table_name} WHERE item = ?"
        return self._fetch_one(query, (item,))

    def update(self, item: str, data: str) -> Optional[Dict]:
        """Updates or creates a record based on the unique 'item' column."""
        with get_db_connection() as conn:
            try:
                query = "INSERT OR REPLACE INTO preferences (item, data) VALUES (?, ?)"
                conn.execute(query, (item, data))
                conn.commit()
                return self.get_by_item(item)
            except sqlite3.IntegrityError:
                return None
