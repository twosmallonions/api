from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile

from tso_api.dependency import (
    GetUser,
    RecipeAssetServiceDep,
    RecipeImportServiceDep,
    RecipeServiceDep,
    recipe_list_query_parameters,
)
from tso_api.models.base import ListResponse
from tso_api.models.query_params import RecipeQueryParams
from tso_api.models.recipe import ImportRecipe, RecipeCreate, RecipeFull, RecipeLight, RecipeUpdate

router = APIRouter(prefix='/api/recipe', tags=['Recipe'])


@router.get('/')
async def get_all_recipes_for_user(
    user: GetUser,
    recipe_service: RecipeServiceDep,
    query_params: Annotated[RecipeQueryParams, Depends(recipe_list_query_parameters)],
) -> ListResponse[RecipeLight]:
    return await recipe_service.get_recipes_by_user(user, query_params)


@router.get('/{collection_id}/{recipe_id}')
async def get_recipe_by_id(
    user: GetUser, recipe_id: UUID, collection_id: UUID, recipe_service: RecipeServiceDep
) -> RecipeFull:
    return await recipe_service.get_by_id(recipe_id, user)


@router.post('/{collection_id}')
async def create_recipe_in_collection(
    recipe_create: RecipeCreate, user: GetUser, collection_id: UUID, recipe_service: RecipeServiceDep
) -> RecipeFull:
    return await recipe_service.create(recipe_create, user, collection_id)


@router.post('/{collection_id}/import')
async def import_recipe_from_url(
    recipe_import: ImportRecipe, user: GetUser, collection_id: UUID, recipe_import_service: RecipeImportServiceDep
) -> RecipeFull:
    return await recipe_import_service.scrape_and_save_recipe(str(recipe_import.url), user, collection_id)


@router.put('/{collection_id}/{recipe_id}')
async def update_recipe(
    recipe_update: RecipeUpdate, user: GetUser, collection_id: UUID, recipe_id: UUID, recipe_service: RecipeServiceDep
) -> RecipeFull:
    return await recipe_service.update_recipe(recipe_id, recipe_update, user)


@router.put('/{collection_id}/{recipe_id}/cover')
async def add_thumbnail_to_recipe(
    file: UploadFile,
    collection_id: UUID,
    recipe_id: UUID,
    user: GetUser,
    recipe_service: RecipeServiceDep,
    recipe_asset_service: RecipeAssetServiceDep,
) -> RecipeFull:
    await recipe_asset_service.add_cover_image_to_recipe(recipe_id, collection_id, user, file.file, file.filename)

    return await recipe_service.get_by_id(recipe_id, user)
