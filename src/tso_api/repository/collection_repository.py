from uuid import UUID

import uuid6
from psycopg import AsyncCursor
from psycopg.rows import DictRow


async def new_collection(name: str, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
tso.collections (id, name)
VALUES (%s, %s)"""

    collection_id = uuid6.uuid7()

    await cur.execute(query, (collection_id, name))

    return collection_id


async def get_collection_by_id(id: UUID, cur: AsyncCursor[DictRow]):
    query = "SELECT * FROM tso.collections WHERE id = %s"

    return await (await cur.execute(query, (id,))).fetchone()


async def get_collection_by_name(name: str, cur: AsyncCursor[DictRow]):
    query = "SELECT * FROM tso.collections WHERE name = %s"

    return await (await cur.execute(query, (name,))).fetchone()


async def get_collections_for_user(cur: AsyncCursor[DictRow]):
    query = "SELECT c.* FROM tso.collections c"

    res = await cur.execute(query)
    return await res.fetchall()


async def add_collection_member(collection_id: UUID, user_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO tso.collection_members
(collection, "user")
VALUES (%s, %s)"""
    await cur.execute(query, (collection_id, user_id))

async def add_collection_owner(collection_id: UUID, user_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO tso.collection_members
(collection, "user", owner)
VALUES (%s, %s, true)"""
    await cur.execute(query, (collection_id, user_id))


async def edit_collection(collection_id: UUID, new_name: str, cur: AsyncCursor[DictRow]):
    query = """UPDATE tso.collections
    SET name = %s
    WHERE id = %s"""

    await cur.execute(query, (new_name, collection_id))
