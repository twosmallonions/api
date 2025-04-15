from uuid import UUID

from tso_api.models.base import Timestamps, TSOBase
from tso_api.models.user import User


class CollectionBase(TSOBase):
    name: str


class CollectionCreate(CollectionBase):
    pass


class CollectionFull(CollectionBase, Timestamps):
    id: UUID


class CollectionMember(TSOBase):
    id: int
    collection: CollectionFull
    user: User
