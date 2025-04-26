# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints
from recipe import Timestamps

from tso_api.models.base import TSOBase


class ShoppingListEntryBase(TSOBase):
    name: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    note: str


class ShoppingListEntryCreate(ShoppingListEntryBase):
    pass


class ShoppingListEntry(ShoppingListEntryBase):
    id: UUID
    completed: bool


class ShoppingListBase(TSOBase):
    title: Annotated[str, StringConstraints(min_length=1, max_length=1000)]


class ShoppingListCreate(ShoppingListBase):
    pass


class ShoppingList(ShoppingListBase, Timestamps):
    id: UUID
    owner: str


class ShoppingListWithEntries(ShoppingList):
    entries: list[ShoppingListEntry] = []
    entries_num: int
