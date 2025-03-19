from datetime import datetime

from base import TSOBase


class DatabaseUser(TSOBase):
    id: int
    subject: str
    issuer: str
    created_at: datetime


class User(DatabaseUser):
    username: str
    email: str

