from psycopg import AsyncConnection
from uuid6 import uuid7

from tso_api.service.base_service import ResourceNotFoundError
from tso_api.models.user import DatabaseUser

CREATE_USER_QUERY = "INSERT INTO users (id, subject, issuer) VALUES (%s, %s, %s)"
GET_USER_QUERY = "SELECT id, subject, issuer, created_at FROM users WHERE issuer = %s and subject = %s"


async def create_user(subject: str, issuer: str, conn: AsyncConnection):
    async with conn.transaction(), conn.cursor() as cur:
        await cur.execute(CREATE_USER_QUERY, (uuid7(), subject, issuer))

    return await get_user(subject, issuer, conn)


async def get_user(subject: str, issuer: str, conn: AsyncConnection):
    async with conn.transaction(), conn.cursor() as cur:
        res = await (await cur.execute(GET_USER_QUERY, (issuer, subject))).fetchone()

        if res is None:
            raise ResourceNotFoundError(subject)

    return DatabaseUser(id=res[0], subject=res[1], issuer=res[2], created_at=res[3])


async def get_or_create_user(subject: str, issuer: str, conn: AsyncConnection):
    try:
        return await get_user(subject, issuer, conn)
    except ResourceNotFoundError:
        return await create_user(subject, issuer, conn)
