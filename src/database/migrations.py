import asyncio
import aiosqlite
from database.engine import get_db_connection, setup_database


async def migration_1():
    """Create initial tables."""
    print("==> Running migration 1: Creating initial tables...")
    await setup_database()


async def migration_2():
    """Add indexes to tables."""
    print("==> Running migration 2: Adding indexes...")
    async with get_db_connection() as db:
        await db.executescript('''
        CREATE INDEX IF NOT EXISTS idx_category_name ON categories(name);
        CREATE INDEX IF NOT EXISTS idx_category_type ON categories(type);
        CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_transaction_type ON transactions(type);
        CREATE INDEX IF NOT EXISTS idx_transaction_category ON transactions(category);
        CREATE INDEX IF NOT EXISTS idx_transaction_account ON transactions(account);
        CREATE INDEX IF NOT EXISTS idx_preferences_item ON preferences(item);
        ''')


MIGRATIONS = [
    migration_1,
    migration_2,
    # Add more migration functions here as needed
]

async def get_current_version() -> int:
    """Get the current schema version from the database, safely handling non-existent tables."""
    try:
        async with get_db_connection() as conn:
            async with conn.execute("SELECT version FROM schema_version") as cursor:
                row = await cursor.fetchone()
                return row['version'] if row else 0
    except aiosqlite.OperationalError:
        print("==> schema_version table not found, assuming initial run.")
        return 0

async def migrate():
    """Apply all pending migrations."""
    current_version = await get_current_version()
    
    if current_version == 0:
        print("==> Initializing database...")
        await migration_1()
        current_version = 1
        async with get_db_connection() as conn:
            await conn.execute("INSERT INTO schema_version (version) VALUES (?)", (current_version,))
            await conn.commit()
    
    for i in range(current_version, len(MIGRATIONS)):
        migration_func = MIGRATIONS[i]
        migration_version = i + 1
        
        print(f"==> Applying migration {migration_version}...")
        await migration_func()
        
        async with get_db_connection() as conn:
            await conn.execute("UPDATE schema_version SET version = ?", (migration_version,))
            await conn.commit()

    print("==> Migrations completed successfully. <==")


if __name__ == "__main__":
    asyncio.run(migrate())
