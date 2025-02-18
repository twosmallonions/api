import asyncio
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tso_api.db import db_pool
from tso_api.repository.recipe_repository import ResourceNotFoundError

from .routers.recipe import router as recipe_router


class DBMigrationError(Exception):
    msg: str = 'failed to migrate database: {}'

    def __init__(self, err: str) -> None:
        super().__init__(self.msg.format(err))


@asynccontextmanager
async def lifespan(_instance: FastAPI):
    dbmate_path = shutil.which('dbmate')
    if dbmate_path is None:
        msg = 'dbmate not found'
        raise DBMigrationError(msg)

    proc = await asyncio.create_subprocess_shell(
        f'{dbmate_path} up', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _stdout, stderr = await proc.communicate()
    code = await proc.wait()
    if code != 0:
        raise DBMigrationError(stderr.decode())
    await db_pool.open(timeout=5)
    yield
    await db_pool.close(timeout=5)


app = FastAPI(lifespan=lifespan)
app.include_router(recipe_router)


@app.get('/boot/')
def hello_world():
    return {'hello': 'world'}


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "resource_not_found", "resource": exc.resource, "message": str(exc)}
    )
