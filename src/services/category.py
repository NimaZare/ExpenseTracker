from services.base import BaseService
from database.engine import get_db_connection
from typing import Dict, Optional, Generator


class CategoryService(BaseService):
    def __init__(self):
        super().__init__("categories")

    def get_by_name(self, name: str) -> Optional[Dict]:
        """Fetches a category by its unique name."""
        query = "SELECT * FROM categories WHERE name = ? AND is_active = 1"
        return self._fetch_one(query, (name,))
    
    def stream_categories(self, batch_size: int = 500) -> Generator[Dict, None]:
        """Stream categories from the database in batches."""
        with get_db_connection() as db:
            with db.execute('SELECT * FROM categories WHERE is_active = 1') as cursor:
                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(row)

