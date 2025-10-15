import uuid
import datetime
import sqlite3
from typing import Dict, List, Optional
from database.engine import get_db_connection 


class BaseService:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _execute(self, query: str, params=()) -> List[Dict]:
        """Helper to execute a query and return all results."""
        with get_db_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return [dict(row) for row in cursor.fetchall()] 

    def _fetch_one(self, query: str, params=()) -> Optional[Dict]:
        """Helper to fetch a single result."""
        with get_db_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def create(self, **kwargs) -> Optional[Dict]:
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

        with get_db_connection() as conn:
            try:
                conn.execute(query, list(kwargs.values()))
                conn.commit()
                return self.get_by_id(record_id)
            except sqlite3.IntegrityError: 
                return None

    def get_by_id(self, record_id: str) -> Optional[Dict]:
        """Fetches a single record by its ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ? AND is_active = 1"
        return self._fetch_one(query, (record_id,)) 
    
    def get_all(self) -> List[Dict]:
        """Fetches all records from the table."""
        query = f"SELECT * FROM {self.table_name} WHERE is_active = 1"
        return self._execute(query)

    def update(self, record_id: str, **kwargs) -> Optional[Dict]:
        """Updates an existing record."""
        kwargs['updated_at'] = datetime.datetime.now().isoformat()
        set_clause = ', '.join([f"{key} = ?" for key in kwargs])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        params = list(kwargs.values()) + [record_id]

        with get_db_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            if cursor.rowcount > 0:
                return self.get_by_id(record_id)
            return None

    def delete(self, record_id: str) -> bool:
        """Deletes a record (soft-delete)."""
        query = f"UPDATE {self.table_name} SET is_active = 0 WHERE id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(query, (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        
