from psycopg_pool import AsyncConnectionPool

from tso_api.config import settings

db_pool = AsyncConnectionPool(str(settings.database_url), open=False)


async def get_connection():
    async with db_pool.connection(5) as conn:
        await conn.set_autocommit(True)
        yield conn
