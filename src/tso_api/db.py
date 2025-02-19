import os
from typing import Annotated

from fastapi import Depends
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool


class ConfigurationError(Exception):
    msg: str = 'Missing or invalid configuration: {}'

    def __init__(self, err: str) -> None:
        super().__init__(self.msg.format(err))


def get_db_url():
    return os.getenv('DATABASE_URL') or ""


db_pool = AsyncConnectionPool(get_db_url(), open=False)


async def get_connection():
    async with db_pool.connection(5) as conn:
        await conn.set_autocommit(True)
        yield conn


DBConn = Annotated[AsyncConnection, Depends(get_connection)]
