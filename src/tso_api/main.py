import asyncio
import shutil
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from tso_api.auth import AuthenticationError, OIDCAuth, User
from tso_api.config import settings
from tso_api.db import db_pool
from tso_api.repository.recipe_repository import ResourceNotFoundError
from tso_api.routers.recipe import router as recipe_router


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


@app.exception_handler(ResourceNotFoundError)
def resource_not_found_handler(_request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={'error': 'resource_not_found', 'resource': exc.resource, 'message': str(exc)},
    )


@app.exception_handler(AuthenticationError)
def authentication_error_handler(_request: Request, exc: AuthenticationError):
    www_authenticate_header = f'Bearer realm="tso"'
    if exc.www_authenticate_error:
        www_authenticate_header += f' error="{exc.www_authenticate_error}"'

    if exc.error_description:
        www_authenticate_header += f' error_description="{exc.error_description}"'
    return Response(status_code=401, headers={'www-authenticate': www_authenticate_header})


oidc_auth = OIDCAuth(str(settings.oidc_well_known), ['RS256'])
user = Annotated[User, Depends(oidc_auth)]


@app.get('/test')
def auth(user: Annotated[User, Depends(oidc_auth)]):
    return user.sub
