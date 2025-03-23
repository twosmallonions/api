import os
import random
import shutil
import string
import subprocess
import uuid
from collections.abc import Awaitable, Callable, Generator

from psycopg import AsyncConnection
import pytest
from psycopg_pool import AsyncConnectionPool
from testcontainers.postgres import PostgresContainer

from tso_api.models.user import User
from tso_api.repository import collection_repository, user_repository

postgres = PostgresContainer('postgres:17')




@pytest.fixture
def ascii_letter_string() -> Callable[[int], str]:
    return lambda n: ''.join(random.choices(string.ascii_letters, k=n))


@pytest.fixture(scope='module')
def setup_db() -> Generator[str]:
    db_url = ''
    if os.environ.get('DATABASE_URL'):
        db_url = os.environ['DATABASE_URL']
    else:
        postgres.start()
        db_url = f'postgresql://{postgres.username}:{postgres.password}@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}/{postgres.dbname}?sslmode=disable'
    dbmate_path = shutil.which('dbmate')
    if dbmate_path is None:
        raise Exception("dbmate not found")
    subprocess.run([dbmate_path, '-u', db_url, 'up'], check=True)
    yield db_url
    postgres.stop()


@pytest.fixture(scope='module')
async def db_pool(setup_db: str):
    db_pool = AsyncConnectionPool(setup_db, open=False)
    await db_pool.open(wait=True, timeout=5)
    yield db_pool
    await db_pool.close()


@pytest.fixture
async def conn(db_pool: AsyncConnectionPool):
    async with db_pool.connection() as conn:
        await conn.set_autocommit(True)
        yield conn


UserFn = Callable[[AsyncConnection], Awaitable[User]]
@pytest.fixture
def user():
    async def __create(conn: AsyncConnection) -> User:
        user = await user_repository.create_user(str(uuid.uuid4()), 'https://idp.example.com', conn)
        return User(id=user.id, subject=user.subject, issuer=user.issuer, created_at=user.created_at, username='test', email='test@test.com')

    return __create


@pytest.fixture
def user_col_fn(user: UserFn):
    user_fn = user

    async def __create(conn: AsyncConnection) -> tuple[User, uuid.UUID]:
        user = await user_fn(conn)
        col = await collection_repository.new_collection("Default", user, conn)
        return (user, col.id)

    return __create


@pytest.fixture
async def user_col(user_col_fn: Callable[[AsyncConnection], Awaitable[tuple[User, uuid.UUID]]], conn: AsyncConnection):
    return await user_col_fn(conn)
