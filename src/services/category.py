from services.base import BaseService
from database.engine import get_db_connection
from typing import Dict, Optional, AsyncGenerator


class CategoryService(BaseService):
    def __init__(self):
        super().__init__("categories")

    async def get_by_name(self, name: str) -> Optional[Dict]:
        """Fetches a category by its unique name."""
        query = "SELECT * FROM categories WHERE name = ? AND is_active = 1"
        return await self._fetch_one(query, (name,))
    

    async def stream_categories(self, batch_size: int = 500) -> AsyncGenerator[Dict, None]:
        """Stream categories from the database in batches."""
        async with get_db_connection() as db:
            async with db.execute('SELECT * FROM categories WHERE is_active = 1') as cursor:
                while True:
                    rows = await cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(row)

