# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

import uuid6
from psycopg import AsyncCursor
from psycopg.rows import DictRow

from tso_api.repository import NoneAfterInsertError, NoneAfterUpdateError


async def new_collection(name: str, cur: AsyncCursor[DictRow]):
    query = 'INSERT INTO tso.collection VALUES (%s, %s) RETURNING *'

    collection_id = uuid6.uuid7()

    res = await (await cur.execute(query, (collection_id, name))).fetchone()

    if res is None:
        msg = 'collection'
        raise NoneAfterInsertError(msg)

    return res


async def get_collection_by_id(coll_id: UUID, cur: AsyncCursor[DictRow]):
    query = 'SELECT * FROM tso.collection WHERE id = %s'

    return await (await cur.execute(query, (coll_id,))).fetchone()


async def get_collection_by_name(name: str, cur: AsyncCursor[DictRow]):
    query = 'SELECT * FROM tso.collection WHERE name = %s'

    return await (await cur.execute(query, (name,))).fetchone()


async def get_collections_for_user(cur: AsyncCursor[DictRow]):
    query = 'SELECT c.* FROM tso.collection c'

    res = await cur.execute(query)
    return await res.fetchall()


async def add_collection_member(collection_id: UUID, user_id: UUID, cur: AsyncCursor[DictRow]):
    query = 'INSERT INTO tso.collection_member VALUES (%s, %s)'
    await cur.execute(query, (collection_id, user_id))


async def add_collection_owner(collection_id: UUID, user_id: UUID, cur: AsyncCursor[DictRow]):
    query = 'INSERT INTO tso.collection_member VALUES (%s, %s, true)'
    await cur.execute(query, (collection_id, user_id))


async def edit_collection(collection_id: UUID, new_name: str, cur: AsyncCursor[DictRow]):
    query = """UPDATE tso.collection
    SET name = %s
    WHERE id = %s
    RETURNING *"""

    res = await (await cur.execute(query, (new_name, collection_id))).fetchone()

    if res is None:
        msg = 'coll'
        raise NoneAfterUpdateError(msg, collection_id)

    return res
