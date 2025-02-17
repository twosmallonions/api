import os
import subprocess
from turtle import pos
from typing import Generator
from psycopg_pool import AsyncConnectionPool
import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer # type: ignore
from tso_api.repository.recipe_repository import RecipeRepository
from tso_api.routers.recipe import RecipeCreate

postgres = PostgresContainer("postgres:17")

@pytest.fixture(scope="session")
def setup_db() -> Generator[str, None, None]:
    postgres.start()
    db_url = f"postgresql://{postgres.username}:{postgres.password}@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}/{postgres.dbname}?sslmode=disable" 
    os.environ['DATABASE_URL'] = db_url
    subprocess.run(["dbmate", "up"], check=True)
    yield db_url
    postgres.stop()

@pytest_asyncio.fixture(scope="session")
async def db_pool(setup_db: str):
    print(f'connecting to db at {setup_db}')
    db_pool = AsyncConnectionPool(setup_db, open=False)
    await db_pool.open(wait=True, timeout=5)
    yield db_pool
    await db_pool.close()