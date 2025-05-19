# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from tso_api.config import settings
from tso_api.db import db_pool, db_pool_fn
from tso_api.exceptions import ApiError, ApiHttpError, AuthenticationError
from tso_api.routers.asset import router as asset_router
from tso_api.routers.collection import router as collection_router
from tso_api.routers.recipe import router as recipe_router
from tso_api.routers.user import router as user_router


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
    db_pool_fn_ret = db_pool_fn()
    await db_pool_fn_ret.open()
    yield
    await db_pool_fn_ret.close()
    await db_pool.close(timeout=5)


enable_openapi = '/docs/' if settings.enable_openapi else None
app = FastAPI(lifespan=lifespan, docs_url=enable_openapi, redoc_url=None)
app.include_router(collection_router)
app.include_router(recipe_router)
app.include_router(asset_router)
app.include_router(user_router)
origins = ['*']

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*']
)


@app.get('/')
def healthcheck():
    return {'ok': True}


@app.exception_handler(ApiError)
def handle_api_error(_request: Request, exc: ApiError):
    error_response = ApiHttpError(error=str(exc), detail=exc.detail(), id=exc.error_id()).model_dump_json(
        exclude_none=True
    )
    headers = {'content-type': 'application/json'} | exc.http_headers()
    if isinstance(exc, AuthenticationError):
        print(f'auth error: {exc.error_message}')
    return Response(status_code=exc.status, content=error_response, headers=headers)
