# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


from functools import cache
from typing import Annotated, Any

from fastapi import Depends
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from tso_api.auth import get_user
from tso_api.db import db_pool_fn, get_connection
from tso_api.models.user import User
from tso_api.service.collection_service import CollectionService
from tso_api.service.recipe_asset import RecipeAssetService
from tso_api.service.recipe_service import RecipeService
from tso_api.service.user_service import UserService

GetUser = Annotated[User, Depends(get_user)]
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
