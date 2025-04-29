# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


from functools import cache
from typing import Annotated, Any

from fastapi import Depends, Header
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from tso_api.auth import JWT, OIDCAuth
from tso_api.config import get_settings
from tso_api.db import db_pool_fn, get_connection
from tso_api.models.user import User
from tso_api.service.collection_service import CollectionService
from tso_api.service.recipe_asset import RecipeAssetService
from tso_api.service.recipe_service import RecipeService
from tso_api.service.user_service import UserService

DBConn = Annotated[AsyncConnection, Depends(get_connection)]


@cache
def get_recipe_service(db_pool_fn: Annotated[AsyncConnectionPool[Any], Depends(db_pool_fn)]):
    return RecipeService(db_pool_fn)


@cache
def get_recipe_asset_service(db_pool_fn: Annotated[AsyncConnectionPool[Any], Depends(db_pool_fn)]):
    return RecipeAssetService(db_pool_fn)


@cache
def get_collection_service(db_pool_fn: Annotated[AsyncConnectionPool[Any], Depends(db_pool_fn)]):
    return CollectionService(db_pool_fn)


@cache
def get_user_service(db_pool_fn: Annotated[AsyncConnectionPool[Any], Depends(db_pool_fn)]):
    return UserService(db_pool_fn)


RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
RecipeAssetServiceDep = Annotated[RecipeAssetService, Depends(get_recipe_asset_service)]
CollectionServiceDep = Annotated[CollectionService, Depends(get_collection_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@cache
def oidc_auth():
    return OIDCAuth(str(get_settings().oidc_well_known))


def jwt(oidc_auth: Annotated[OIDCAuth, Depends(oidc_auth)], authorization: Annotated[str | None, Header(include_in_schema=False)]):
    return oidc_auth(authorization)


async def get_user(jwt: Annotated[JWT, Depends(jwt)], user_service: UserServiceDep) -> User:
    return await user_service.get_or_create_user(jwt.sub, jwt.iss)


GetUser = Annotated[User, Depends(get_user)]
