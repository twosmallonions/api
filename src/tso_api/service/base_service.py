# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


class ServiceError(Exception):
    pass


class ResourceNotFoundError(Exception):
    msg: str = 'resource not found: {0}'
    resource: str

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(self.msg.format(resource))


class BaseService:
    def __init__(self, pool: AsyncConnectionPool[Any]) -> None:
        self.pool = pool

    @asynccontextmanager
    async def _begin(self, user_id: UUID):
        async with self.pool.connection() as conn, conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
            await cur.execute('SET ROLE tso_api_user')
            await cur.execute('SELECT tso.set_uid(%s)', (user_id,))
            yield cur

    @asynccontextmanager
    async def _begin_unsafe(self):
        async with self.pool.connection() as conn, conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
            yield cur
