# tso_api/service/shopping_list_service.py
# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

from psycopg.rows import DictRow

from tso_api.models.shopping_list import (
    ShoppingListCreate,
    ShoppingListEntry,
    ShoppingListEntryCreate,
    ShoppingListWithEntries,
)
from tso_api.models.user import User
from tso_api.repository import shopping_list_repository
from tso_api.service.base_service import BaseService


class ShoppingListService(BaseService):
    async def create_list(
        self, list_data: ShoppingListCreate, collection_id: UUID, user: User
    ) -> ShoppingListWithEntries:
        # The user's identity is passed to _begin for RLS
        async with self._begin(user.id) as cur:
            row = await shopping_list_repository.create_list(list_data.title, collection_id, cur)
            return _shopping_list_from_row(row)

    async def update_list(
        self, list_data: ShoppingListCreate, list_id: UUID, collection_id: UUID, user: User
    ) -> ShoppingListWithEntries:
        async with self._begin(user.id) as cur:
            row = await shopping_list_repository.update_list(list_data.title, list_id, collection_id, cur)
            return _shopping_list_from_row(row)

    async def add_entry_to_list(
        self, entry_data: ShoppingListEntryCreate, list_id: UUID, user: User
    ) -> ShoppingListEntry:
        async with self._begin(user.id) as cur:
            # The repository only uses the 'name' field for insertion
            row = await shopping_list_repository.add_entry_to_list(entry_data.name, list_id, cur)
            return _list_entry_from_row(row)

    async def set_list_entry_completed(self, entry_id: UUID, list_id: UUID, user: User) -> None:
        async with self._begin(user.id) as cur:
            await shopping_list_repository.set_list_entry_completed(entry_id, list_id, cur)

    async def unset_list_entry_completed(self, entry_id: UUID, list_id: UUID, user: User) -> None:
        async with self._begin(user.id) as cur:
            await shopping_list_repository.unset_list_entry_completed(entry_id, list_id, cur)

    async def get_list(self, list_id: UUID, user: User) -> ShoppingListWithEntries:
        async with self._begin(user.id) as cur:
            row = await shopping_list_repository.get_list(list_id, cur)
            return _shopping_list_from_row(row)


def _list_entry_from_row(row: DictRow) -> ShoppingListEntry:
    return ShoppingListEntry(
        id=row['id'],
        name=row['name'],
        note=row.get('note', ''),
        created_at=row['created_at'],
        updated_at=row['updated_at'],
        list_id=row['list_id'],
        completed=row['completed'],
        completed_at=row.get('completed_at'),
    )


def _shopping_list_from_row(row: DictRow) -> ShoppingListWithEntries:
    entries = [_list_entry_from_row(entry) for entry in row.get('entries', [])]
    return ShoppingListWithEntries(
        id=row['id'],
        title=row['title'],
        collection_id=row['collection_id'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
        entries=entries,
        entries_num=row.get('num_entries', len(entries)),
    )
