from pydoc import text
import random
import re
import uuid
from collections.abc import Callable

import pytest
from psycopg import AsyncConnection

from tso_api.models.recipe import IngredientUpdate, InstructionUpdate, RecipeCreate, RecipeFull, RecipeUpdate
from tso_api.repository import recipe_repository


@pytest.fixture
def recipe_create(ascii_letter_string: Callable[[int], str]) -> RecipeCreate:
    return RecipeCreate(
        title=ascii_letter_string(7),
        description=ascii_letter_string(50),
        cook_time=random.randint(0, 80),
        prep_time=random.randint(0, 80),
        recipe_yield=ascii_letter_string(5),
    )


async def test_get_missing_recipe_by_slug_exception(conn: AsyncConnection):
    with pytest.raises(recipe_repository.ResourceNotFoundError):
        await recipe_repository.get_recipe_by_slug(str(uuid.uuid4()), str(uuid.uuid4()), conn)


async def test_get_missing_recipe_by_id_exception(conn: AsyncConnection):
    with pytest.raises(recipe_repository.ResourceNotFoundError):
        await recipe_repository.get_recipe_by_id(uuid.uuid4(), str(uuid.uuid4()), conn)


async def test_get_recipe_id(recipe_create: RecipeCreate, owner: str, conn: AsyncConnection):
    recipe = await recipe_repository.create_recipe(recipe_create, owner, conn)

    fetched_recipe = await recipe_repository.get_recipe_by_id(recipe.id, recipe.owner, conn)

    assert fetched_recipe.id == recipe.id


async def test_toggle_recipe_liked(recipe_create: RecipeCreate, owner: str, conn: AsyncConnection):
    recipe = await recipe_repository.create_recipe(recipe_create, owner, conn)

    await recipe_repository.update_liked(True, recipe.id, owner, conn)

    updated_recipe = await recipe_repository.get_recipe_by_slug(recipe.slug, owner, conn)

    assert updated_recipe.liked

    await recipe_repository.update_liked(False, recipe.id, owner, conn)

    updated_recipe = await recipe_repository.get_recipe_by_slug(recipe.slug, owner, conn)

    assert not updated_recipe.liked


async def test_insert_recipe(conn: AsyncConnection):
    test_create = RecipeCreate(
        title='Test4',
        description='my recipe description',
        cook_time=5,
        prep_time=5,
        recipe_yield='5 servings',
        liked=True,
    )

    recipe = await recipe_repository.create_recipe(test_create, str(uuid.uuid4()), conn)

    assert recipe.title == test_create.title
    assert recipe.description == test_create.description
    assert recipe.cook_time == test_create.cook_time
    assert recipe.prep_time == test_create.prep_time
    assert recipe.total_time == (test_create.cook_time or 0) + (test_create.prep_time or 0)
    assert recipe.recipe_yield == test_create.recipe_yield
    assert recipe.liked


async def test_insert_recipe_missing_prep_time(conn: AsyncConnection):
    test_create = RecipeCreate(
        title='Test4', description='my recipe description', cook_time=5, recipe_yield='5 servings'
    )

    recipe = await recipe_repository.create_recipe(test_create, str(uuid.uuid4()), conn)

    assert recipe.title == test_create.title
    assert recipe.description == test_create.description
    assert recipe.cook_time == test_create.cook_time
    assert recipe.prep_time == test_create.prep_time
    assert recipe.total_time == (test_create.cook_time or 0) + (test_create.prep_time or 0)
    assert recipe.recipe_yield == test_create.recipe_yield


async def test_insert_recipe_with_instructions_and_ingredients(conn: AsyncConnection):
    test_create = RecipeCreate(
        title='test_insert_ins_ingre',
        description='my recipe description',
        cook_time=5,
        recipe_yield='5 servings',
        ingredients=['Milk', 'Butter', 'Chocolate'],
        instructions=['Put everything in a bowl', 'Bake for 20 minutes'],
    )

    recipe = await recipe_repository.create_recipe(test_create, str(uuid.uuid4()), conn)
    assert len(recipe.instructions) == 2
    assert len(recipe.ingredients) == 3

    assert recipe.ingredients[0].text == 'Milk'
    assert recipe.ingredients[0].id
    assert recipe.ingredients[2].text == 'Chocolate'


@pytest.fixture
def recipe_update():
    updated_title = 'updated_title'
    updated_description = 'updated description'
    updated_cook_time = 500
    updated_prep_time = 500
    updated_recipe_yield = str(10)
    updated_liked = True

    return RecipeUpdate(
        title=updated_title,
        description=updated_description,
        cook_time=updated_cook_time,
        prep_time=updated_prep_time,
        recipe_yield=str(updated_recipe_yield),
        liked=updated_liked,
    )


def compare_recipe_with_recipe_update(recipe: RecipeFull, recipe_update: RecipeUpdate):
    assert recipe.title == recipe_update.title
    assert recipe.description == recipe_update.description
    assert recipe.cook_time == recipe_update.cook_time
    assert recipe.prep_time == recipe_update.prep_time
    assert recipe.recipe_yield == recipe_update.recipe_yield
    assert recipe.liked == recipe_update.liked
    assert recipe.total_time == (recipe_update.cook_time or 0) + (recipe_update.prep_time or 0)


async def test_update_recipe(
    recipe_create: RecipeCreate, owner: str, conn: AsyncConnection, recipe_update: RecipeUpdate
):
    recipe = await recipe_repository.create_recipe(recipe_create, owner, conn)

    await recipe_repository.update_recipe(recipe_update, owner, recipe.id, conn)

    updated_recipe = await recipe_repository.get_recipe_by_id(recipe.id, owner, conn)

    compare_recipe_with_recipe_update(updated_recipe, recipe_update)


async def test_update_recipe_with_ingredients_and_instruction(
    recipe_create: RecipeCreate, owner: str, conn: AsyncConnection, recipe_update: RecipeUpdate
):
    recipe_create.ingredients = ['Milk', 'Butter', 'Chocolate']
    recipe_create.instructions = ['Put everything in a bowl', 'Bake for 20 minutes']
    recipe = await recipe_repository.create_recipe(recipe_create, owner, conn)

    updated_ingredients: list[IngredientUpdate] = [IngredientUpdate(text=a.text, id=a.id) for a in recipe.ingredients]
    updated_ingredients.insert(0, IngredientUpdate(text='New', id=None))
    updated_ingredients.insert(2, IngredientUpdate(text='New 2', id=None))

    updated_instructions: list[InstructionUpdate] = [
        InstructionUpdate(text=a.text, id=a.id) for a in recipe.instructions
    ]
    updated_instructions.pop(0)
    updated_instructions.insert(0, InstructionUpdate(text='New', id=None))
    updated_instructions.insert(2, InstructionUpdate(text='New 2', id=None))

    recipe_update.instructions = updated_instructions
    recipe_update.ingredients = updated_ingredients

    await recipe_repository.update_recipe(recipe_update, owner, recipe.id, conn)

    updated_recipe = await recipe_repository.get_recipe_by_id(recipe.id, owner, conn)

    compare_recipe_with_recipe_update(updated_recipe, recipe_update)

    for updated, saved in zip(updated_instructions, updated_recipe.instructions, strict=True):
        assert updated.text == saved.text
        if updated.id is not None:
            assert updated.id == saved.id
        else:
            assert saved.id

    for updated, saved in zip(updated_ingredients, updated_recipe.ingredients, strict=True):
        assert updated.text == saved.text

        if updated.id is not None:
            assert updated.id == saved.id
        else:
            assert saved.id
