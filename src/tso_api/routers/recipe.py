
from fastapi import APIRouter

from tso_api.db import DBConn
from tso_api.models.recipe import RecipeCreate, RecipeFull
from tso_api.repository import recipe_repository

router = APIRouter(prefix='/recipe')


@router.get('/{slug}')
async def get_all_recipes(slug: str, db: DBConn) -> RecipeFull:
    return await recipe_repository.get_recipe_by_slug(slug, "123", db)


@router.post('/')
async def create_recipe(recipe_create: RecipeCreate, db: DBConn) -> RecipeFull:
    return await recipe_repository.create_recipe(recipe_create, "123", db)
