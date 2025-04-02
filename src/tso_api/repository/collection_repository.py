from typing import Any
from uuid import UUID

from sqlalchemy.orm import selectinload
import uuid6
from sqlalchemy import Row, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from tso_api.models.collection import CollectionFull
from tso_api.models.user import User
from tso_api.schema.recipe_schema import CollectionSchema, UserSchema


async def new_collection(name: str, session: AsyncSession):
    collection_id = uuid6.uuid7()
    collection = CollectionSchema(
        id=collection_id,
        name=name,
        slug=name.lower(),
    )

    session.add(collection)
    return collection

async def get_collections_for_user(user: User, sess: AsyncSession):
    stmt = select(UserSchema).where(UserSchema.id == user.id).options(selectinload(UserSchema.collections))
    res = await sess.execute(stmt)
    return res.scalar_one().collections
