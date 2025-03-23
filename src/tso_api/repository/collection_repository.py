from typing import Any
from uuid import UUID
from psycopg.rows import DictRow, dict_row
import uuid6
from psycopg import AsyncConnection, AsyncCursor, cursor

from tso_api.models.user import User
from tso_api.models.collection import CollectionFull


async def new_collection_cur(name: str, user: User, cur: AsyncCursor[Any]):
    collection_insert = """INSERT INTO
collections (id, name, slug, owner)
VALUES (%s, %s, %s, %s)
RETURNING id, name, slug, owner, created_at, updated_at"""

    collection_id = uuid6.uuid7()
    res = await (await cur.execute(collection_insert, (collection_id, name, name.lower(), user.id))).fetchone()
    if res is None:
        raise Exception('ahh')
    return __collection_from_row(res)


async def new_collection(name: str, user: User, db: AsyncConnection):
    async with db.transaction(), db.cursor(row_factory=dict_row) as cur:
        return await new_collection_cur(name, user, cur)


async def get_collections_for_user(user: User, db: AsyncConnection):
    async with db.transaction(), db.cursor(row_factory=dict_row) as cur:
        res = await cur.execute("""SELECT c.* FROM collections c
LEFT JOIN collection_members cm
ON cm.collection = c.id
WHERE cm.user = %(user_id)s OR c.owner = %(user_id)s""", {'user_id': user.id})
        rows = await res.fetchall()

        return [__collection_from_row(row) for row in rows]


async def add_collection_member(collection: UUID, user: User, db: AsyncConnection):
    async with db.transaction(), db.cursor() as cur:
        await cur.execute("""INSERT INTO collection_members
(collection, "user")
VALUES (%s, %s)""", (collection, user.id))


def __collection_from_row(row: DictRow) -> CollectionFull:
    return CollectionFull(
        name=row['name'],
        id=row['id'],
        slug=row['slug'],
        owner=row['owner']
    )
