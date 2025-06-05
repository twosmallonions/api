# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

from psycopg.rows import DictRow

from tso_api.models.collection import CollectionCreate, CollectionFull
from tso_api.models.user import User
from tso_api.repository import collection_repository
from tso_api.service.base_service import BaseService


class CollectionService(BaseService):
    async def new_collection(self, collection: CollectionCreate, user: User) -> CollectionFull:
        async with self._begin(user.id) as cur:
            coll = await collection_repository.new_collection(collection.name, cur)
            coll_id = coll['id']

            await collection_repository.add_collection_member(coll_id, user.id, cur)

        return _collection_from_row(coll)

    async def get_collections_for_user(self, user: User) -> list[CollectionFull]:
        async with self._begin(user.id) as cur:
            rows = await collection_repository.get_collections_for_user(cur)

        return [_collection_from_row(row) for row in rows]

    async def add_collection_member(self, collection_id: UUID, user: User):
        async with self._begin(user.id) as cur:
            await collection_repository.add_collection_member(collection_id, user.id, cur)

    async def get_collections_for_user_with_members(self, user: User):
        async with self._begin(user.id) as cur:
            await collection_repository.get_collections_for_user_with_collection_members(cur)


def _collection_from_row(row: DictRow) -> CollectionFull:
    return CollectionFull(name=row['name'], id=row['id'], created_at=row['created_at'], updated_at=row['updated_at'])
