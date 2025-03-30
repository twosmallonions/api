
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from tso_api.auth import get_user
from tso_api.db import get_connection
from tso_api.models.user import User

user = Annotated[User, Depends(get_user)]
DBConn = Annotated[AsyncConnection, Depends(get_connection)]
