from uuid import UUID

from tso_api.models.base import TSOBase
from tso_api.models.user import User


class CollectionBase(TSOBase):
    name: str


class CollectionFull(CollectionBase):
    id: UUID
    slug: str
    owner: int


class CollectionMember(TSOBase):
    id: int
    collection: CollectionFull
    user: User
