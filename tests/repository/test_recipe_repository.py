import uuid
from psycopg_pool import AsyncConnectionPool
import pytest
from tso_api.repository.recipe_repository import RecipeRepository
from tso_api.routers.recipe import RecipeCreate

@pytest.fixture(scope="session")
def recipe_repository(db_pool: AsyncConnectionPool):
    return RecipeRepository(db_pool)

@pytest.mark.asyncio
async def test_insert_recipe(recipe_repository: RecipeRepository):
    test_create = RecipeCreate(title="Test4")

    recipe = await recipe_repository.create_recipe(test_create, str(uuid.uuid4()))

    assert recipe.title == "Test4"