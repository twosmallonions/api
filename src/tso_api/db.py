from contextlib import asynccontextmanager

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tso_api.config import settings

url_object = URL.create(
    "postgresql+psycopg",
    username=settings.postgres_username,
    password=settings.postgres_password,
    host=settings.postgres_host,
    database=settings.postgres_db,
    port=settings.postgres_port,
)

engine = create_async_engine(url_object, echo=True)
Session = async_sessionmaker(engine)


@asynccontextmanager
async def get_connection():
    async with engine.connect() as conn:
        yield conn
