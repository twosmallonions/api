# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from psycopg import AsyncCursor
from psycopg.rows import DictRow
from uuid6 import uuid7

from tso_api.repository import NoneAfterInsertError

GET_USER_QUERY = 'SELECT id, subject, issuer, created_at FROM tso.account WHERE issuer = %s and subject = %s'


async def create_user(subject: str, issuer: str, cur: AsyncCursor[DictRow]):
    query = (
        'INSERT INTO tso.account (id, subject, issuer) VALUES (%s, %s, %s) RETURNING id, subject, issuer, created_at'
    )
    res = await (await cur.execute(query, (uuid7(), subject, issuer))).fetchone()

    if res is None:
        msg = 'user'
        raise NoneAfterInsertError(msg)

    return res


async def get_user(subject: str, issuer: str, cur: AsyncCursor[DictRow]):
    return await (await cur.execute(GET_USER_QUERY, (issuer, subject))).fetchone()
