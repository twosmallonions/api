# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import os
import random
import shutil
import string
import subprocess
import uuid
from collections.abc import Awaitable, Callable, Generator

import psycopg
import pytest
from psycopg import AsyncConnection, AsyncCursor
from psycopg.rows import DictRow, dict_row
from testcontainers.postgres import PostgresContainer

from tso_api.models.user import User
from tso_api.repository import collection_repository, user_repository

postgres = PostgresContainer('postgres:17')


AsciiLetterString = Callable[[int], str]


@pytest.fixture
def ascii_letter_string() -> AsciiLetterString:
    return lambda n: ''.join(random.choices(string.ascii_letters, k=n))


@pytest.fixture(scope="package")
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


@pytest.fixture
async def conn(setup_db: str):
    return await psycopg.AsyncConnection.connect(setup_db)


UserFn = Callable[[AsyncCursor[DictRow]], Awaitable[User]]


@pytest.fixture
def user():
    async def __create(cur: AsyncCursor[DictRow]) -> User:
        subject = str(uuid.uuid4())
        issuer = 'https://idp.example.com'
        await user_repository.create_user(subject, issuer, str(uuid.uuid4()), cur)
        user = await user_repository.get_user(subject, issuer, cur)
        assert user
        return User(id=user['id'], subject=user['subject'], issuer=user['issuer'], created_at=user['created_at'], display_name=user['display_name'])

    return __create


UserColFn = Callable[[AsyncCursor[DictRow]], Awaitable[tuple[User, uuid.UUID]]]


@pytest.fixture
def user_col_fn(user: UserFn) -> UserColFn:
    user_fn = user

    async def __create(cur: AsyncCursor[DictRow]) -> tuple[User, uuid.UUID]:
        user = await user_fn(cur)
        coll = await collection_repository.new_collection("Default", cur)
        await collection_repository.add_collection_owner(coll['id'], user.id, cur)
        return (user, coll['id'])

    return __create


@pytest.fixture
async def user_col(user_col_fn: UserColFn, conn: AsyncConnection):
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        return await user_col_fn(cur)
