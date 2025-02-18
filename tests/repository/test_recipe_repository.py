import uuid

from psycopg import AsyncConnection

from tso_api.models.recipe import RecipeCreate
from tso_api.repository import recipe_repository


async def test_insert_recipe(conn: AsyncConnection):
    test_create = RecipeCreate(
        title='Test4',
        description='my recipe description',
        cook_time=5,
        prep_time=5,
        recipe_yield='5 servings'
    )

    recipe = await recipe_repository.create_recipe(test_create, str(uuid.uuid4()), conn)

    assert recipe.title == test_create.title
    assert recipe.description == test_create.description
    assert recipe.cook_time == test_create.cook_time
    assert recipe.prep_time == test_create.prep_time
    assert recipe.total_time == (test_create.cook_time or 0) + (test_create.prep_time or 0)
    assert recipe.recipe_yield == test_create.recipe_yield


async def test_insert_recipe_missing_prep_time(conn: AsyncConnection):
    test_create = RecipeCreate(
        title='Test4',
        description='my recipe description',
        cook_time=5,
        recipe_yield='5 servings'
    )

    recipe = await recipe_repository.create_recipe(test_create, str(uuid.uuid4()), conn)

    assert recipe.title == test_create.title
    assert recipe.description == test_create.description
    assert recipe.cook_time == test_create.cook_time
    assert recipe.prep_time == test_create.prep_time
    assert recipe.total_time == (test_create.cook_time or 0) + (test_create.prep_time or 0)
    assert recipe.recipe_yield == test_create.recipe_yield
