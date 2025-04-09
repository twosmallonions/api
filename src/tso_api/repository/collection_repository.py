from uuid import UUID

import uuid6
from psycopg import AsyncCursor
from psycopg.rows import DictRow

from tso_api.models.collection import CollectionCreate
from tso_api.models.user import User


async def new_collection(name: str, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
collections (id, name)
VALUES (%s, %s)"""

    collection_id = uuid6.uuid7()
     
    await cur.execute(query, (collection_id, name))
    

async def get_collection_by_name(name: str, cur: AsyncCursor[DictRow]):
    query = "SELECT * FROM collections WHERE name = %s"

    return await (await cur.execute(query, (name,))).fetchone()


async def get_collections_for_user(user_id: UUID, cur: AsyncCursor[DictRow]):
    query = """SELECT c.* FROM collections c
LEFT JOIN collection_members cm
ON cm.collection = c.id
WHERE c.id IN (SELECT collection FROM collection_members WHERE "user" = %(user_id)s)"""

    res = await cur.execute(query, {'user_id': user_id})
    return await res.fetchall()


async def add_collection_member(collection_id: UUID, user_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO collection_members
(collection, "user")
VALUES (%s, %s)"""
    await cur.execute(query, (collection_id, user_id))
