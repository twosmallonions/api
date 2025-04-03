from uuid import UUID

import uuid6
from psycopg import AsyncCursor
from psycopg.rows import DictRow

from tso_api.models.collection import CollectionCreate
from tso_api.models.user import User


async def new_collection(collection: CollectionCreate, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
collections (id, name, slug)
VALUES (%s, %s, %s)
RETURNING id, name, slug, created_at, updated_at"""

    collection_id = uuid6.uuid7()
    return await (
        await cur.execute(query, (collection_id, collection.name, collection.name.lower()))
    ).fetchone()


async def get_collections_for_user(user: User, cur: AsyncCursor[DictRow]):
    query = """SELECT c.* FROM collections c
LEFT JOIN collection_members cm
ON cm.collection = c.id
WHERE c.id IN (SELECT collection FROM collection_members WHERE "user" = %(user_id)s)"""

    res = await cur.execute(query, {'user_id': user.id})
    return await res.fetchall()


async def add_collection_member(collection_id: UUID, user: User, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO collection_members
(collection, "user")
VALUES (%s, %s)"""
    await cur.execute(query, (collection_id, user.id))
