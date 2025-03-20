from datetime import datetime

from tso_api.models.base import TSOBase


class DatabaseUser(TSOBase):
    id: int
    subject: str
    issuer: str
    created_at: datetime


class User(DatabaseUser):
    username: str
    email: str

