import aiosqlite
from typing import Dict, Optional
from services.base import BaseService
from database.engine import get_db_connection


class ThemeService(BaseService):
    def __init__(self):
        super().__init__("preferences")

    async def get_by_item(self, item: str) -> Optional[Dict]:
        """Fetches a preference by its unique item."""
        query = f"SELECT * FROM {self.table_name} WHERE item = ?"
        return await self._fetch_one(query, (item,))

    async def update(self, item: str, data: str) -> Optional[Dict]:
        """Updates or creates a record based on the unique 'item' column."""
        async with get_db_connection() as conn:
            try:
                query = "INSERT OR REPLACE INTO preferences (item, data) VALUES (?, ?)"
                await conn.execute(query, (item, data))
                await conn.commit()
                return await self.get_by_item(item)
            except aiosqlite.IntegrityError:
                return None
