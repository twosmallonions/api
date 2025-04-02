import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tso_api.models.user import User
from tso_api.schema.recipe_schema import Base, CollectionSchema
from tso_api.service.collection_service import CollectionService


async def test_create_collection():
    engine = create_async_engine('postgresql+psycopg://postgres:postgres@localhost:5432/postgres', echo=True)
    Session = async_sessionmaker(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    service = CollectionService(Session)

    res = await service.new_collection()

async def test_get_collection():
    engine = create_async_engine('postgresql+psycopg://postgres:postgres@localhost:5432/postgres', echo=True)
    Session = async_sessionmaker(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    service= CollectionService(Session)
    
    user = User(id=UUID('0823f2a72ae84872be1ecc341c1c7006'), subject='test', issuer='test', created_at=datetime.datetime.now(datetime.UTC))

    res = await service.get_collections_for_user(user)
    assert len(res) == 1
    assert res[0].id == UUID('4c078f6eb5b94db6b87adf10afa80d21')
