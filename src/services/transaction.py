from services.base import BaseService
from typing import Dict, List, Generator, Optional
from database.engine import get_db_connection


class TransactionService(BaseService):
    def __init__(self):
        super().__init__("transactions")

    def get_dashboard_summary(self, month: int, year: int) -> Dict:
        """Calculates total balance, monthly income, and monthly expenses."""
        month_filter = f"{year}-{month:02d}-%"
        
        query_balance = """
        SELECT SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) - 
               SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) AS total_balance
        FROM transactions WHERE is_active = 1;
        """
        
        query_metrics = f"""
        SELECT 
            SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) AS monthly_expenses,
            SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) AS monthly_income
        FROM transactions
        WHERE is_active = 1 AND date LIKE ?;
        """
        
        balance_row = self._fetch_one(query_balance)
        metrics_row = self._fetch_one(query_metrics, (month_filter,))
        
        return {
            'total_balance': balance_row['total_balance'] if balance_row and balance_row['total_balance'] is not None else 0.0,
            'monthly_expenses': metrics_row['monthly_expenses'] if metrics_row and metrics_row['monthly_expenses'] is not None else 0.0,
            'monthly_income': metrics_row['monthly_income'] if metrics_row and metrics_row['monthly_income'] is not None else 0.0,
        }

    def get_spending_breakdown(self, month: int, year: int) -> Dict:
        """Gets expense totals grouped by category for the chart."""
        month_filter = f"{year}-{month:02d}-%"
        query = """
        SELECT 
            c.name AS category_name, 
            SUM(t.amount) AS total_amount
        FROM transactions t
        JOIN categories c ON t.category = c.id
        WHERE t.type = 'Expense' 
            AND t.is_active = 1 
            AND t.date LIKE ?
        GROUP BY c.name
        ORDER BY total_amount DESC;
        """
        rows = self._execute(query, (month_filter,))
        
        return {row['category_name']: row['total_amount'] for row in rows}

    def get_recent_transactions(self, limit: int = 5) -> List[Dict]:
        """Fetches the N most recent transactions for the side panel."""
        query = """
        SELECT 
            t.description, 
            t.date, 
            t.amount, 
            t.type
        FROM transactions t
        WHERE t.is_active = 1
        ORDER BY t.date DESC
        LIMIT ?;
        """
        
        return self._execute(query, (limit,))

    
    def get_by_date(self, date_str: str) -> List[Dict]:
        """Fetches transactions for a specific date."""
        query = f"SELECT * FROM {self.table_name} WHERE date = ? AND is_active = 1"
        return self._execute(query, (date_str,))

    def stream_by_category(self, category: str, batch_size: int = 500) -> Generator[Dict, None, None]:
        """Stream transactions for a specific category from the database in batches."""
        with get_db_connection() as db:
            with db.execute('SELECT * FROM transactions WHERE category = ? AND is_active = 1', (category,)) as cursor:
                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(row)

    def stream_transactions(self, batch_size: int = 500) -> Generator[Dict, None, None]:
        """Stream transactions from the database in batches."""
        with get_db_connection() as db:
            with db.execute('SELECT * FROM transactions WHERE is_active = 1 ORDER BY date DESC') as cursor:
                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(row)

    def add_transaction(self, transaction_data: Dict) -> Optional[Dict]:
        """Add a new transaction to the database"""
        return self.create(**{
            'type': transaction_data['type'],
            'amount': transaction_data['amount'],
            'date': transaction_data['date'],
            'category': transaction_data['category'],
            'account': transaction_data['account'],
            'description': transaction_data.get('description', '')
        })
    
    def get_transactions_by_type(self, transaction_type: str) -> List[Dict]:
        """Get all transactions of a specific type (Expense, Income, Transfer)"""
        query = f"SELECT * FROM {self.table_name} WHERE type = ? AND is_active = 1 ORDER BY date DESC"
        return self._execute(query, (transaction_type,))
    
    def get_transactions_by_category(self, category: str) -> List[Dict]:
        """Get all transactions in a specific category"""
        query = f"SELECT * FROM {self.table_name} WHERE category = ? AND is_active = 1 ORDER BY date DESC"
        return self._execute(query, (category,))
    
    def get_transactions_by_account(self, account: str) -> List[Dict]:
        """Get all transactions for a specific account"""
        query = f"SELECT * FROM {self.table_name} WHERE account = ? AND is_active = 1 ORDER BY date DESC"
        return self._execute(query, (account,))
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get transactions within a date range"""
        query = f"SELECT * FROM {self.table_name} WHERE date BETWEEN ? AND ? AND is_active = 1 ORDER BY date DESC"
        return self._execute(query, (start_date, end_date))
    
    def get_total_by_type(self, transaction_type: str) -> float:
        """Calculate total amount for a specific transaction type"""
        query = f"SELECT SUM(amount) as total FROM {self.table_name} WHERE type = ? AND is_active = 1"
        result = self._fetch_one(query, (transaction_type,))
        return result['total'] if result and result['total'] else 0.0

    def get_total_count(self) -> int:
        """Get total count of active transactions"""
        query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE is_active = 1"
        result = self._fetch_one(query)
        return result['count'] if result else 0
