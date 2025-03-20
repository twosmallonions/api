from uuid import UUID

from base import TSOBase
from user import User


class CollectionBase(TSOBase):
    name: str


class CollectionFull(CollectionBase):
    id: UUID
    slug: str
    owner: 'CollectionMember'


class CollectionMember(TSOBase):
    id: int
    collection: CollectionFull
    user: User
