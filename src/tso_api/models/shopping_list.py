# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from tso_api.models.base import Timestamps, TSOBase


class ShoppingListEntryBase(TSOBase):
    name: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    note: Annotated[str, StringConstraints(max_length=1000)] = ''


class ShoppingListEntryCreate(ShoppingListEntryBase):
    pass


class ShoppingListEntry(ShoppingListEntryBase, Timestamps):
    id: UUID
    completed: bool
    completed_at: datetime | None = None


class ShoppingListBase(TSOBase):
    title: Annotated[str, StringConstraints(min_length=1, max_length=250)]


class ShoppingListCreate(ShoppingListBase):
    pass


class ShoppingList(ShoppingListBase, Timestamps):
    id: UUID
    collection_id: UUID


class ShoppingListWithEntries(ShoppingList):
    entries: list[ShoppingListEntry] = []
    entries_num: int = 0
