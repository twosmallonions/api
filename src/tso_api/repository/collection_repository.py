import uuid6
from psycopg import AsyncConnection

from tso_api.models.user import User


async def new_collection(name: str, user: User, db: AsyncConnection):
    await db.set_deferrable(True)
    COLLECTION_INSERT = """INSERT INTO
    collections (id, name, slug)
VALUES (%s, %s, %s)"""
    COLLECTION_MEMBERS_INSERT = """INSERT INTO
    collection_members (collection, "user")
VALUES (%s, %s) RETURNING id"""
    UPDATE_COLLECTION = """UPDATE collections SET owner = %s WHERE id = %s"""

    async with db.transaction(), db.cursor() as cur:
        collection_id = uuid6.uuid7()
        await cur.execute(COLLECTION_INSERT, (collection_id, name, name.lower()))
        res = await (await cur.execute(COLLECTION_MEMBERS_INSERT, (collection_id, user.id))).fetchone()
        if res is None:
            raise Exception('asdasd')
        collection_members_id = res[0]

        await cur.execute(UPDATE_COLLECTION, (collection_members_id, collection_id))
