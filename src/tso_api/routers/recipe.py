from uuid import UUID
from fastapi import APIRouter, UploadFile

from tso_api.db import DBConn
from tso_api.models.recipe import RecipeCreate, RecipeFull
from tso_api.repository import recipe_repository
from tso_api.service import recipe_asset

router = APIRouter(prefix='/recipe')


@router.get('/{slug}')
async def get_recipe_by_slug(slug: str, db: DBConn) -> RecipeFull:
    return await recipe_repository.get_recipe_by_slug(slug, '123', db)


@router.post('/')
async def create_recipe(recipe_create: RecipeCreate, db: DBConn) -> RecipeFull:
    return await recipe_repository.create_recipe(recipe_create, '123', db)


@router.post('/{recipe_id}')
async def get_recipe_by_id(recipe_id: UUID, db: DBConn) -> RecipeFull:
    return await recipe_repository.get_recipe_by_id(recipe_id, '123', db)

@router.post('/{recipe_id}/cover')
async def add_cover_image_to_recipe(recipe_id: UUID, file: UploadFile, db: DBConn):
    recipe_asset.add_cover_image_to_recipe(recipe_id, '1234', file, file.filename, db)
