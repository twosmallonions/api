# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


from typing import Annotated

from fastapi import Depends
from psycopg import AsyncConnection

from tso_api.auth import get_user
from tso_api.db import db_pool, get_connection
from tso_api.models.user import User

GetUser = Annotated[User, Depends(get_user)]
DBConn = Annotated[AsyncConnection, Depends(get_connection)]
