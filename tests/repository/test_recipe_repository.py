# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import random
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from psycopg import AsyncConnection, AsyncCursor
from psycopg.errors import InsufficientPrivilege, IntegrityError
from psycopg.rows import DictRow, dict_row

from tests.repository.conftest import AsciiLetterString, UserFn
from tso_api.models.recipe import RecipeCreate, RecipeUpdate
from tso_api.models.user import User
from tso_api.repository import collection_repository, recipe_repository

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


async def set_perms(user_id: UUID, cur: AsyncCursor[DictRow]):
    await cur.execute('SET LOCAL ROLE tso_api_user')
    await cur.execute('SELECT tso.set_uid(%s)', (user_id, ))


async def create_recipe(user: User, coll_id: UUID, recipe_create_fn: RecipeCreateFn, cur: AsyncCursor[DictRow]) -> tuple[dict[str, Any], RecipeCreate]:
    recipe_create = recipe_create_fn()
    recipe_create.recipe_yield = None
    await set_perms(user.id, cur)
    return await recipe_repository.create_recipe(recipe_create, coll_id, user.id, cur), recipe_create


def verify_recipe(recipe: DictRow | None, coll: UUID, created_by: User, recipe_create: RecipeCreate):
    assert recipe
    assert recipe['collection_id'] == coll
    assert recipe['created_by'] == created_by.id
    assert recipe['title'] == recipe_create.title


async def test_create_recipe(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], conn: AsyncConnection):
    user, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        recipe, recipe_create = await create_recipe(user, coll, recipe_create_fn, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        recipe = await (await cur.execute('SELECT * FROM tso.recipe WHERE id = %s', (recipe['id'], ))).fetchone()

    verify_recipe(recipe, coll, user, recipe_create)


@pytest.mark.parametrize('title_length', [0, 300, 500])
async def test_create_recipe_title_length(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], ascii_letter_string: AsciiLetterString, title_length: int, conn: AsyncConnection):
    user, coll = user_col
    recipe_create = recipe_create_fn()
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        recipe_create.title = ascii_letter_string(title_length)
        with pytest.raises(IntegrityError):
             await recipe_repository.create_recipe(recipe_create, coll, user.id, cur)


async def test_collection_members_can_add_recipes(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], user: UserFn, conn: AsyncConnection):
    _, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        second_user = await user(cur)
        await collection_repository.add_collection_member(coll, second_user.id, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(second_user.id, cur)
        recipe, recipe_create = await create_recipe(second_user, coll, recipe_create_fn, cur)

    verify_recipe(recipe, coll, second_user, recipe_create)


async def test_non_collection_members_cant_add_recipes(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], user: UserFn, conn: AsyncConnection):
    _, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        second_user = await user(cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(second_user.id, cur)
        with pytest.raises(InsufficientPrivilege):
            await create_recipe(second_user, coll, recipe_create_fn, cur)


async def test_get_recipe_by_id(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], conn: AsyncConnection):
    user, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        created_recipe, recipe_create = await create_recipe(user, coll, recipe_create_fn, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        recipe = await recipe_repository.get_recipe_by_id(created_recipe['id'], cur)

    verify_recipe(recipe, coll, user, recipe_create)


async def test_collection_member_can_read_recipes_in_collection(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], user: UserFn, conn: AsyncConnection):
    u, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        second_user = await user(cur)
        await set_perms(u.id, cur)
        await collection_repository.add_collection_member(coll, second_user.id, cur)
        created_recipe, recipe_create = await create_recipe(u, coll, recipe_create_fn, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(second_user.id, cur)
        recipe = await recipe_repository.get_recipe_by_id(created_recipe['id'], cur)

    verify_recipe(recipe, coll, u, recipe_create)


async def test_update_recipe(recipe_create_fn: RecipeCreateFn, recipe_update: RecipeUpdate, user_col: tuple[User, UUID], conn: AsyncConnection):
    user, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        created_recipe, _ = await create_recipe(user, coll, recipe_create_fn, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        updated_recipe = await recipe_repository.update_recipe(recipe_update, created_recipe['id'], cur)


    compare_recipe_with_recipe_update(updated_recipe, recipe_update)


async def test_collection_member_can_update_recipes_in_collection(recipe_create_fn: RecipeCreateFn, user_col: tuple[User, UUID], user: UserFn, conn: AsyncConnection, recipe_update: RecipeUpdate,):
    u, coll = user_col
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        second_user = await user(cur)
        await set_perms(u.id, cur)
        created_recipe, recipe_create = await create_recipe(u, coll, recipe_create_fn, cur)
        await collection_repository.add_collection_member(coll, second_user.id, cur)


    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(second_user.id, cur)
        updated_recipe = await recipe_repository.update_recipe(recipe_update, created_recipe['id'], cur)

    compare_recipe_with_recipe_update(updated_recipe, recipe_update)
