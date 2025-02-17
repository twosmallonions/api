from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from .routers.recipe import router as recipe_router

DB_URL = "postgres://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable"
db_pool = AsyncConnectionPool(DB_URL)
app = FastAPI()
app.include_router(recipe_router)