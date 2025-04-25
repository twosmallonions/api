from uuid import UUID

from fastapi import APIRouter, UploadFile

from tso_api.dependency import GetUser
from tso_api.models.recipe import RecipeCreate, RecipeFull, RecipeLight, RecipeUpdate
from tso_api.service import recipe_asset_service, recipe_service

router = APIRouter(prefix='/api/recipe')


@router.get('/')
async def get_all_recipes_for_user(user: GetUser) -> list[RecipeLight]:
    return await recipe_service.get_recipes_by_user(user)


@router.get('/{collection_id}/{recipe_id}')
async def get_recipe_by_id(user: GetUser, recipe_id: UUID, collection_id: UUID) -> RecipeFull:
    return await recipe_service.get_by_id(recipe_id, user)


@router.post('/{collection_id}')
async def create_recipe_in_collection(recipe_create: RecipeCreate, user: GetUser, collection_id: UUID) -> RecipeFull:
    return await recipe_service.create(recipe_create, user, collection_id)


@router.put('/{collection_id}/{recipe_id}')
async def update_recipe(recipe_update: RecipeUpdate, user: GetUser, collection_id: UUID, recipe_id: UUID) -> RecipeFull:
    return await recipe_service.update_recipe(recipe_id, recipe_update, user)


@router.put('/{collection_id}/{recipe_id}/cover')
async def add_thumbnail_to_recipe(file: UploadFile, collection_id: UUID, recipe_id: UUID, user: GetUser) -> RecipeFull:
    await recipe_asset_service.add_cover_image_to_recipe(recipe_id, collection_id, user, file)

    return await recipe_service.get_by_id(recipe_id, user)
