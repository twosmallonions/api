
from typing import Annotated

from fastapi import Depends
from psycopg import AsyncConnection

from tso_api.auth import User, oidc_auth
from tso_api.db import get_connection

user = Annotated[User, Depends(oidc_auth)]
DBConn = Annotated[AsyncConnection, Depends(get_connection)]
