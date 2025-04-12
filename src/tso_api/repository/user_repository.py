from psycopg import AsyncConnection, AsyncCursor
from psycopg.rows import DictRow
from uuid6 import uuid7

from tso_api.service.base_service import ResourceNotFoundError
from tso_api.models.user import DatabaseUser

GET_USER_QUERY = "SELECT id, subject, issuer, created_at FROM tso.users WHERE issuer = %s and subject = %s"


async def create_user(subject: str, issuer: str, cur: AsyncCursor[DictRow]):
    query = "INSERT INTO tso.users (id, subject, issuer) VALUES (%s, %s, %s) RETURNING id, subject, issuer, created_at"
    return await (await cur.execute(query, (uuid7(), subject, issuer))).fetchone()


async def get_user(subject: str, issuer: str, cur: AsyncCursor[DictRow]):
    return await (await cur.execute(GET_USER_QUERY, (issuer, subject))).fetchone()


async def get_or_create_user(subject: str, issuer: str, conn: AsyncConnection):
    try:
        return await get_user(subject, issuer, conn)
    except ResourceNotFoundError:
        return await create_user(subject, issuer, conn)
