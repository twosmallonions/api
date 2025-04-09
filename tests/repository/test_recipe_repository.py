from copy import deepcopy
import random
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from psycopg import AsyncCursor
from psycopg.errors import IntegrityError
from psycopg.rows import DictRow

from tso_api.models.recipe import RecipeCreate, RecipeUpdate
from tso_api.models.user import User
from tso_api.repository import recipe_repository

RecipeCreateFn = Callable[[], RecipeCreate]


@pytest.fixture
def recipe_create_fn(ascii_letter_string: Callable[[int], str]) -> RecipeCreateFn:
    def __run() -> RecipeCreate:
        return RecipeCreate(
            title=ascii_letter_string(7),
            note=ascii_letter_string(50),
            cook_time=random.randint(0, 80),
            prep_time=random.randint(0, 80),
            recipe_yield=ascii_letter_string(5),
        )
    return __run


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
        note=updated_description,
        cook_time=updated_cook_time,
        prep_time=updated_prep_time,
        recipe_yield=str(updated_recipe_yield),
        liked=updated_liked,
    )


def compare_recipe_with_recipe_update(recipe: dict[str, Any], recipe_update: RecipeUpdate):
    assert recipe['title'] == recipe_update.title
    assert recipe['note'] == recipe_update.note
    assert recipe['cook_time'] == recipe_update.cook_time
    assert recipe['prep_time'] == recipe_update.prep_time
    assert recipe['yield'] == recipe_update.recipe_yield
    assert recipe['liked'] == recipe_update.liked
    assert recipe['total_time'] == (recipe_update.cook_time or 0) + (recipe_update.prep_time or 0)


async def test_create_recipe(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], cur: AsyncCursor[DictRow]):
    user, coll = user_col
    recipe_create = recipe_create_fn()
    recipe_id = await recipe_repository.create_recipe(recipe_create, coll, user.id, cur)

    recipe = await (await cur.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id, ))).fetchone()

    assert recipe
    assert recipe['collection'] == coll
    assert recipe['created_by'] == user.id
    assert recipe['title'] == recipe_create.title


async def test_create_recipe_empty_title(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], cur: AsyncCursor[DictRow]):
    user, coll = user_col
    recipe_create = recipe_create_fn()
    recipe_create.title = ''
    with pytest.raises(IntegrityError):
        await recipe_repository.create_recipe(recipe_create, coll, user.id, cur)


async def test_get_recipe_by_id(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], cur: AsyncCursor[DictRow]):
    user, coll = user_col
    recipe_create = recipe_create_fn()
    recipe_id = await recipe_repository.create_recipe(recipe_create, coll, user.id, cur)

    recipe = await recipe_repository.get_recipe_by_id(recipe_id, user.id, cur)

    assert recipe
    assert recipe['collection'] == coll
    assert recipe['created_by'] == user.id
    assert recipe['title'] == recipe_create.title


async def test_update_recipe(recipe_create_fn: RecipeCreateFn, recipe_update: RecipeUpdate, user_col: tuple[User, UUID], cur: AsyncCursor[DictRow]):
    user, coll = user_col
    recipe_create = recipe_create_fn()
    recipe_id = await recipe_repository.create_recipe(recipe_create, coll, user.id, cur)

    await recipe_repository.update_recipe(recipe_update, recipe_id, cur)

    recipe_updated = await recipe_repository.get_recipe_by_id(recipe_id, user.id, cur)
    assert recipe_updated

    compare_recipe_with_recipe_update(recipe_updated, recipe_update)


async def test_get_recipe_light_by_user(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], cur: AsyncCursor[DictRow]):
    user, coll = user_col

    ids: set[UUID] = set()
    for _ in range(20):
        recipe_create = recipe_create_fn()
        recipe_id = await recipe_repository.create_recipe(recipe_create, coll, user.id, cur)
        ids.add(recipe_id)

    recipes = await recipe_repository.get_recipes_light_by_owner(user.id, cur)

    assert {recipe['id'] for recipe in recipes} == ids
