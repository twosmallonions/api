# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


from functools import cache
from typing import Annotated, Any

from fastapi import Depends
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from tso_api import config
from tso_api.auth import JWT, OIDCAuth
from tso_api.config import get_settings
from tso_api.db import db_pool_fn, get_connection
from tso_api.models.query_params import BaseSort, CursorPagination, RecipeQueryParams, RecipeSortField, SortOrder
from tso_api.models.user import User
from tso_api.service.collection_service import CollectionService
from tso_api.service.recipe_asset import RecipeAssetService
from tso_api.service.recipe_import_service import RecipeImportService
from tso_api.service.recipe_service import RecipeService
from tso_api.service.shopping_list_service import ShoppingListService
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


@cache
def get_shopping_list_service(db_pool_fn: Annotated[AsyncConnectionPool[Any], Depends(db_pool_fn)]):
    return ShoppingListService(db_pool_fn)


RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
RecipeAssetServiceDep = Annotated[RecipeAssetService, Depends(get_recipe_asset_service)]
CollectionServiceDep = Annotated[CollectionService, Depends(get_collection_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ShoppingListServiceDep = Annotated[ShoppingListService, Depends(get_shopping_list_service)]


@cache
def get_recipe_import_service(
    db_pool_fn: Annotated[AsyncConnectionPool[Any], Depends(db_pool_fn)],
    recipe_service: RecipeServiceDep,
    recipe_asset_service: RecipeAssetServiceDep,
):
    return RecipeImportService(
        db_pool_fn, recipe_service, recipe_asset_service, config.get_settings().http_scraper_user_agent
    )


RecipeImportServiceDep = Annotated[RecipeImportService, Depends(get_recipe_import_service)]


oidc_auth = OIDCAuth(str(get_settings().oidc_well_known))


async def get_user(jwt: Annotated[JWT, Depends(oidc_auth)], user_service: UserServiceDep) -> User:
    return await user_service.get_or_create_user(jwt)


GetUser = Annotated[User, Depends(get_user)]


def cursor_pagination(limit: int = 50, cursor: str | None = None):
    return CursorPagination(limit=limit, cursor=cursor)


def recipe_list_query_parameters(
    pagination: Annotated[CursorPagination, Depends(cursor_pagination)],
    order: SortOrder = SortOrder.DESC,
    field: RecipeSortField = RecipeSortField.CREATED_AT,
    search: str | None = None,
):
    base_sort = BaseSort(order=order, field=field)

    return RecipeQueryParams(pagination=pagination, sort=base_sort, search=search)
