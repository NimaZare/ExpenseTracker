from services.base import BaseService
from typing import Dict, List, Generator
from database.engine import get_db_connection


class TransactionService(BaseService):
    def __init__(self):
        super().__init__("transactions")

    def get_by_date(self, date_str: str) -> List[Dict]:
        """Fetches transactions for a specific date."""
        query = f"SELECT * FROM {self.table_name} WHERE date = ? AND is_active = 1"
        return self._execute(query, (date_str,))

    def stream_by_category(self, category: str, batch_size: int = 500) -> Generator[Dict, None]:
        """Stream transactions for a specific category from the database in batches."""
        with get_db_connection() as db:
            with db.execute(f'SELECT * FROM transactions WHERE category = ? AND is_active = 1', (category,)) as cursor:
                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(row)

    def stream_transactions(self, batch_size: int = 500) -> Generator[Dict, None]:
        """Stream transactions from the database in batches."""
        with get_db_connection() as db:
            with db.execute('SELECT * FROM transactions WHERE is_active = 1') as cursor:
                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(row)

