from typing import Any
from uuid import UUID
from sqlalchemy import Row, insert, select, or_
import uuid6
from sqlalchemy.ext.asyncio import AsyncConnection

from tso_api.schema import t_collections, t_collection_members

from tso_api.models.user import User
from tso_api.models.collection import CollectionFull


async def new_collection_cur(name: str, user: User, conn: AsyncConnection):
    collection_id = uuid6.uuid7()
    stmt = (
        insert(t_collections)
        .values(id=collection_id, name=name, slug=name.lower(), owner=user.id)
        .returning(t_collections)
    )

    res = await conn.execute(stmt)
    res = res.fetchone()

    if res is None:
        raise Exception('ahh')
    return __collection_from_row(res)


async def get_collections_for_user(user: User, conn: AsyncConnection):
    stmt = (
        select(t_collections)
        .join(t_collection_members, t_collection_members.c.collection == t_collections.c.id)
        .where(or_(t_collection_members.c.user == user.id, t_collections.c.owner == user.id))
    )

    rows = (await conn.execute(stmt)).fetchall()

    return [__collection_from_row(row) for row in rows]


async def add_collection_member(collection: UUID, user: User, db: AsyncConnection):
    stmt = insert(t_collections).values(collection=collection, user=user.id)
    await db.execute(stmt)


def __collection_from_row(row: Row[Any]) -> CollectionFull:
    return CollectionFull.model_validate(row, from_attributes=True)
