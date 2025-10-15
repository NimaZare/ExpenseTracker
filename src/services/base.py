import uuid
import datetime
import aiosqlite
from typing import Dict, List, Optional
from database.engine import get_db_connection


class BaseService:
    def __init__(self, table_name: str):
        self.table_name = table_name

    async def _execute(self, query: str, params=()) -> List[Dict]:
        """Helper to execute a query and return all results."""
        async with get_db_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return [dict(row) for row in await cursor.fetchall()]

    async def _fetch_one(self, query: str, params=()) -> Optional[Dict]:
        """Helper to fetch a single result."""
        async with get_db_connection() as conn:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create(self, **kwargs) -> Optional[Dict]:
        """Creates a new record in the table."""
        record_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()

        kwargs.update({
            'id': record_id,
            'is_active': 1,
            'created_at': now,
            'updated_at': now
        })

        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

        async with get_db_connection() as conn:
            try:
                await conn.execute(query, list(kwargs.values()))
                await conn.commit()
                return await self.get_by_id(record_id)
            except aiosqlite.IntegrityError:
                return None

    async def get_by_id(self, record_id: str) -> Optional[Dict]:
        """Fetches a single record by its ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ? AND is_active = 1"
        return await self._fetch_one(query, (record_id,))
    
    async def get_all(self) -> List[Dict]:
        """Fetches all records from the table."""
        query = f"SELECT * FROM {self.table_name} WHERE is_active = 1"
        return await self._execute(query)

    async def update(self, record_id: str, **kwargs) -> Optional[Dict]:
        """Updates an existing record."""
        kwargs['updated_at'] = datetime.datetime.now().isoformat()
        set_clause = ', '.join([f"{key} = ?" for key in kwargs])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        params = list(kwargs.values()) + [record_id]

        async with get_db_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            if cursor.rowcount > 0:
                return await self.get_by_id(record_id)
            return None

    async def delete(self, record_id: str) -> bool:
        """Deletes a record (soft-delete)."""
        query = f"UPDATE {self.table_name} SET is_active = 0 WHERE id = ?"
        async with get_db_connection() as conn:
            cursor = await conn.execute(query, (record_id,))
            await conn.commit()
            return cursor.rowcount > 0

