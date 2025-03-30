from collections.abc import AsyncGenerator
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from tso_api.config import settings

url_object = URL.create(
    "postgresql+psycopg",
    username=settings.postgres_username,
    password=settings.postgres_password,
    host=settings.postgres_host,
    database=settings.postgres_db,
    port=settings.postgres_port,
)

engine = create_async_engine(url_object)


async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as conn:
        yield conn
