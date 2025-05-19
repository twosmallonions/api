# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

from tso_api.models.base import Timestamps, TSOBase
from tso_api.models.user import User, UserResponse


class CollectionBase(TSOBase):
    name: str


class CollectionCreate(CollectionBase):
    pass


class CollectionFull(CollectionBase, Timestamps):
    id: UUID


class CollectionWithUsers(CollectionFull):
    users: list[UserResponse]


class CollectionMember(TSOBase):
    id: int
    collection: CollectionFull
    user: User
