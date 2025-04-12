from typing import Any
from uuid import UUID

from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from tso_api.db import db_pool
from tso_api.models.collection import CollectionCreate, CollectionFull
from tso_api.models.user import User
from tso_api.repository import collection_repository
from tso_api.service.base_service import BaseService, ResourceNotFoundError


class CollectionService(BaseService):
    def __init__(self, pool: AsyncConnectionPool[Any]) -> None:
        super().__init__(pool)

    async def new_collection(self, collection: CollectionCreate, user: User) -> CollectionFull:
        async with self.begin() as cur:
            coll_id = await collection_repository.new_collection(collection.name, cur)

            await collection_repository.add_collection_member(coll_id, user.id, cur)

            res = await collection_repository.get_collection_by_id(coll_id, cur)
            if res is None:
                msg = f'collection with id {id} not found'
                raise ResourceNotFoundError(msg)

        return _collection_from_row(res)

    async def get_collections_for_user(self, user: User) -> list[CollectionFull]:
        async with self.begin() as cur:
            rows = await collection_repository.get_collections_for_user(user.id, cur)

        return [_collection_from_row(row) for row in rows]

    async def add_collection_member(self, collection_id: UUID, user: User):
        async with self.begin() as cur:
            await collection_repository.add_collection_member(collection_id, user.id, cur)


def _collection_from_row(row: DictRow) -> CollectionFull:
    return CollectionFull(
        name=row['name'], id=row['id'], slug=row['slug'], created_at=row['created_at'], updated_at=row['updated_at']
    )


