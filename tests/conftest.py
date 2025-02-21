import os
import shutil
import subprocess
from collections.abc import Generator

import pytest
from psycopg_pool import AsyncConnectionPool
from testcontainers.postgres import PostgresContainer

postgres = PostgresContainer('postgres:17')


@pytest.fixture(scope='package')
def setup_db() -> Generator[str]:
    db_url = ''
    if os.environ.get('DATABASE_URL'):
        db_url = os.environ['DATABASE_URL']
    else:
        _ = postgres.start()
        db_url = f'postgresql://{postgres.username}:{postgres.password}@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}/{postgres.dbname}?sslmode=disable'
        os.environ['DATABASE_URL'] = db_url
    dbmate_path = shutil.which('dbmate')
    if dbmate_path is None:
        raise Exception("dbmate not found")
    _ = subprocess.run([dbmate_path, 'up'], check=True)
    yield db_url
    postgres.stop()


@pytest.fixture(scope='package')
async def db_pool(setup_db: str):
    db_pool = AsyncConnectionPool(setup_db, open=False)
    await db_pool.open(wait=True, timeout=5)
    yield db_pool
    await db_pool.close()


@pytest.fixture
async def conn(db_pool: AsyncConnectionPool):
    async with db_pool.connection() as conn:
        yield conn
