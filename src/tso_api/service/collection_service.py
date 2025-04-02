import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tso_api.db import Session
from tso_api.models.collection import CollectionFull, CollectionMember
from tso_api.models.user import User
from tso_api.repository import collection_repository
from tso_api.schema.recipe_schema import UserSchema


class CollectionService:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.Session = sessionmaker

    async def new_collection(self):
        async with self.Session() as sess, sess.begin():
            u = User(id=UUID('0823f2a72ae84872be1ecc341c1c7006'), subject='test', issuer='test', created_at=datetime.datetime.now(datetime.UTC))
            collection = await collection_repository.new_collection(
                'test32562',
                sess
            )
            res = await sess.execute(select(UserSchema).where(UserSchema.id == u.id))
            user = res.scalar_one()
            members = await collection.awaitable_attrs.members
            members.append(user)
            
            return CollectionFull.model_validate(collection, from_attributes=True)
    
    async def get_collections_for_user(self, user: User):
        async with self.Session() as sess, sess.begin():
            colls = await collection_repository.get_collections_for_user(user, sess)
        
            print(colls[0])
            return [CollectionFull.model_validate(collection, from_attributes=True) for collection in colls]

