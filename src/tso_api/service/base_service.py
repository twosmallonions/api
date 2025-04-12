from contextlib import asynccontextmanager

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


class ServiceError(Exception):
    pass


class NoneAfterInsertError(ServiceError):
    msg = '{} was inserted but returned None'

    def __init__(self, resource: str) -> None:
        super().__init__(self.msg.format(resource))


class ResourceNotFoundError(Exception):
    msg: str = 'resource not found: {0}'
    resource: str

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(self.msg.format(resource))


class BaseService:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool = pool

    @asynccontextmanager
    async def begin(self):
        async with self.pool.connection() as conn, conn.transaction(), conn.cursor(row_factory=dict_row) as curr:
            await curr.execute('SET ROLE tso_api_user')
            yield curr
