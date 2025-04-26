# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from uuid import UUID

from tso_api.models.base import TSOBase


class DatabaseUser(TSOBase):
    id: UUID
    subject: str
    issuer: str
    created_at: datetime


class User(DatabaseUser):
    pass
