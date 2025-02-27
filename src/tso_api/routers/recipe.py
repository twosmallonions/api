import io
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File
from fastapi.responses import FileResponse

from tso_api.config import settings
from tso_api.dependency import DBConn, user
from tso_api.models.recipe import RecipeCreate, RecipeFull, RecipeLight
from tso_api.repository import asset_repository, recipe_repository
from tso_api.service import recipe_asset

router = APIRouter(prefix='/api/recipe')


@router.get('/{slug}')
async def get_recipe_by_slug(slug: str, user: user, db: DBConn) -> RecipeFull:
    return await recipe_repository.get_recipe_by_slug(slug, user.sub, db)


@router.post('/')
async def create_recipe(recipe_create: RecipeCreate, user: user, db: DBConn) -> RecipeFull:
    return await recipe_repository.create_recipe(recipe_create, user.sub, db)


@router.get('/')
async def get_recipes_by_owner(user: user, db: DBConn) -> list[RecipeLight]:
    return await recipe_repository.get_recipes_light_by_owner(user.sub, db)


@router.post('/{recipe_id}')
async def get_recipe_by_id(recipe_id: UUID, user: user, db: DBConn) -> RecipeFull:
    return await recipe_repository.get_recipe_by_id(recipe_id, user.sub, db)


@router.post('/{recipe_id}/cover')
async def add_cover_image_to_recipe(recipe_id: UUID, user: user, file: Annotated[bytes, File()], db: DBConn):
    r = io.BytesIO(file)
    await recipe_asset.add_cover_image_to_recipe(recipe_id, user.sub, r, None, db)


@router.get('/asset/{asset_id}')
async def get_asset(asset_id: UUID, user: user, db: DBConn):
    asset = await asset_repository.get_asset_by_id(asset_id, user.sub, db)
    return FileResponse(Path(settings.data_dir) / asset.path, headers={'cache-control': 'max-age=604800, private'})

