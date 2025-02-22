from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AssetBase(BaseModel):
    id: UUID
    path: str
    size: int
    original_name: str | None


class Asset(AssetBase):
    created_at: datetime
