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
