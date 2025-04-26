# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from functools import cache
from psycopg_pool import AsyncConnectionPool

from tso_api import config
from tso_api.config import settings

db_pool = AsyncConnectionPool(str(settings.database_url), open=False)


async def get_connection():
    async with db_pool.connection(5) as conn:
        await conn.set_autocommit(True)
        yield conn


@cache
def db_pool_fn():
    return AsyncConnectionPool(str(config.get_settings().database_url), open=False)

