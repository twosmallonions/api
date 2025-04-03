from uuid import UUID

from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from tso_api.models.collection import CollectionCreate, CollectionFull
from tso_api.models.user import User
from tso_api.repository import collection_repository
from tso_api.service.base_service import BaseService, ResourceNotFoundError


class CollectionService(BaseService):
    def __init__(self, pool: AsyncConnectionPool) -> None:
        super().__init__(pool)

    async def new_collection(self, collection: CollectionCreate, user: User) -> CollectionFull:
        async with self.begin() as cur:
            res = await collection_repository.new_collection(collection, cur)

            if res is None:
                msg = 'collection'
                raise ResourceNotFoundError(msg)

            await collection_repository.add_collection_member(res['id'], user, cur)

        return _collection_from_row(res)

    async def get_collections_for_user(self, user: User) -> list[CollectionFull]:
        async with self.begin() as cur:
            rows = await collection_repository.get_collections_for_user(user, cur)

        return [_collection_from_row(row) for row in rows]

    async def add_collection_member(self, collection_id: UUID, user: User):
        async with self.begin() as cur:
            await collection_repository.add_collection_member(collection_id, user, cur)


def _collection_from_row(row: DictRow) -> CollectionFull:
    return CollectionFull(
        name=row['name'], id=row['id'], slug=row['slug'], created_at=row['created_at'], updated_at=row['updated_at']
    )
