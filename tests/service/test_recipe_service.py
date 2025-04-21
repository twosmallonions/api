# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import random
import string

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from tso_api.models.collection import CollectionCreate
from tso_api.models.recipe import IngredientUpdate, InstructionUpdate, RecipeCreate, RecipeFull, RecipeUpdate
from tso_api.models.user import User
from tso_api.repository import recipe_repository, user_repository
from tso_api.service.collection_service import CollectionService
from tso_api.service.recipe_service import RecipeService


def compare_recipe_with_recipe_update(recipe: RecipeFull, recipe_update: RecipeUpdate):
    assert recipe.title == recipe_update.title
    assert recipe.note == recipe_update.note
    assert recipe.cook_time == recipe_update.cook_time
    assert recipe.prep_time == recipe_update.prep_time
    assert recipe.recipe_yield == recipe_update.recipe_yield
    assert recipe.liked == recipe_update.liked
    assert recipe.total_time == (recipe_update.cook_time or 0) + (recipe_update.prep_time or 0)


def rand_str(n: int):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


async def test_update_recipe(
    recipe_create: RecipeCreate, pool: AsyncConnectionPool, recipe_update: RecipeUpdate
):

    c = CollectionService(pool)
    async with pool.connection() as conn:
        db_user = await user_repository.create_user(rand_str(20), rand_str(20), conn)
        user = User(id=db_user.id, subject=db_user.subject, issuer=db_user.issuer, created_at=db_user.created_at)
        collection = await c.new_collection(CollectionCreate(name=rand_str(20)), user)
    recipe_service = RecipeService(pool)

    recipe_create.collection = collection.id
    recipe_update.collection = collection.id
    recipe = await recipe_service.create(recipe_create, user)

    await recipe_service.update_recipe(recipe.id, recipe_update, user)

    updated_recipe = await recipe_service.get_by_id(recipe.id, user)

    compare_recipe_with_recipe_update(updated_recipe, recipe_update)


async def test_update_recasdipe_with_ingredients_and_instruction(
    recipe_create: RecipeCreate, pool: AsyncConnectionPool, recipe_update: RecipeUpdate
):
    c = CollectionService(pool)
    async with pool.connection() as conn:
        db_user = await user_repository.create_user(rand_str(20), rand_str(20), conn)
        user = User(id=db_user.id, subject=db_user.subject, issuer=db_user.issuer, created_at=db_user.created_at)
        collection = await c.new_collection(CollectionCreate(name=rand_str(20)), user)
    recipe_service = RecipeService(pool)
    recipe_create.collection = collection.id
    recipe_update.collection = collection.id

    recipe_create.ingredients = ['Milk', 'Butter', 'Chocolate']
    recipe_create.instructions = ['Put everything in a bowl', 'Bake for 20 minutes']

    recipe = await recipe_service.create(recipe_create, user)

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

    await recipe_service.update_recipe(recipe.id, recipe_update, user)

    updated_recipe = await recipe_service.get_by_id(recipe.id, user)

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
