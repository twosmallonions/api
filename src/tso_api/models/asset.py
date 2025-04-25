# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel


class AssetBase(BaseModel):
    id: UUID
    path: Path
    size: int
    original_name: str | None


class Asset(AssetBase):
    created_at: datetime


class AssetFile(Asset):
    mime_type: str
    asset_file: bytes
