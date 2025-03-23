import uuid6
from psycopg import AsyncConnection

from tso_api.models.user import User


async def new_collection(name: str, user: User, db: AsyncConnection):
    await db.set_deferrable(True)
    collection_insert = """INSERT INTO
collections (id, name, slug, owner)
VALUES (%s, %s, %s, %s)"""

    async with db.transaction(), db.cursor() as cur:
        collection_id = uuid6.uuid7()
        await cur.execute(collection_insert, (collection_id, name, name.lower(), user.id))
