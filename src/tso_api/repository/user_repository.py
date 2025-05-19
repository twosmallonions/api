# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any
from uuid import UUID

from psycopg import AsyncCursor
from psycopg.rows import DictRow
from uuid6 import uuid7

from tso_api.exceptions import NoneAfterInsertError, NoneAfterUpdateError


async def create_user(subject: str, issuer: str, display_name: str | None, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
    tso.account (id, subject, issuer, display_name)
VALUES (%s, %s, %s, %s)
RETURNING
    id, subject, issuer, created_at, COALESCE(display_name, subject) AS display_name"""
    res = await (await cur.execute(query, (uuid7(), subject, issuer, display_name))).fetchone()

    if res is None:
        msg = 'user'
        raise NoneAfterInsertError(msg)

    return res


async def update_user(account_id: UUID, display_name: str | None, cur: AsyncCursor[DictRow]) -> None:
    query = """UPDATE
    tso.account SET display_name = %s
    WHERE id = %s"""

    res = await cur.execute(query, (display_name, account_id))
    if res.rowcount == 0:
        msg = 'account'
        raise NoneAfterUpdateError(msg, account_id)


async def get_user(subject: str, issuer: str, cur: AsyncCursor[DictRow]):
    query = """SELECT
    id, subject, issuer, created_at, COALESCE(display_name, subject) AS display_name
FROM
    tso.account
WHERE
    issuer = %s and subject = %s"""
    return await (await cur.execute(query, (issuer, subject))).fetchone()


async def get_users(cur: AsyncCursor[DictRow], user_id: UUID | None, search: str | None, limit: int) -> list[DictRow]:
    params: dict[str, Any] = {}
    query = """SELECT
    id, subject, issuer, created_at, COALESCE(display_name, subject) AS display_name
FROM
    tso.account
WHERE 1 = 1"""

    if user_id:
        query += ' AND id != %(account_id)s'
        params |= {'account_id': user_id}

    if search:
        query += " AND display_name ILIKE btrim(%(search)s) || '%%'"
        params |= {'search': search}
    query += " LIMIT %(limit)s"
    params |= {'limit': limit}
    return await (await cur.execute(query, params)).fetchall()
