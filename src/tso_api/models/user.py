# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from uuid import UUID

from tso_api.models.base import TSOBase


class BaseUser(TSOBase):
    id: UUID
    display_name: str


class DatabaseUser(BaseUser):
    subject: str
    issuer: str
    created_at: datetime


class User(DatabaseUser):
    pass


class UserResponse(BaseUser):
    pass


class AddUserToCollection(TSOBase):
    id: UUID
