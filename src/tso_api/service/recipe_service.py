from typing import Any
from uuid import UUID

from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from tso_api.models.recipe import RecipeCreate, RecipeFull, RecipeLight, RecipeUpdate
from tso_api.models.user import User
from tso_api.repository import ingredient_repository, instruction_repository, recipe_repository
from tso_api.service.base_service import BaseService, ResourceNotFoundError


class RecipeService(BaseService):
    def __init__(self, pool: AsyncConnectionPool[Any]) -> None:
        super().__init__(pool)

    async def get_recipes_by_user(self, user: User) -> list[RecipeLight]:
        async with self.begin() as cur:
            recipes = await recipe_repository.get_recipes_light_by_owner(user.id, cur)

        return [_recipe_light_from_row(recipe) for recipe in recipes]

    async def get_by_id(self, recipe_id: UUID, user: User):
        async with self.begin() as cur:
            recipe = await recipe_repository.get_recipe_by_id(recipe_id, user.id, cur)
            if recipe is None:
                msg = f'recipe with id {recipe_id} not found'
                raise ResourceNotFoundError(msg)

            return _recipe_from_row(recipe)

    async def create(self, recipe_create: RecipeCreate, user: User, collection_id: UUID):
        async with self.begin() as cur:
            recipe_id = await recipe_repository.create_recipe(recipe_create, collection_id, user.id, cur)

            for position, ingredient in enumerate(recipe_create.ingredients):
                await ingredient_repository.insert_ingredient(ingredient, position, recipe_id, cur)

            for position, instruction in enumerate(recipe_create.instructions):
                await instruction_repository.insert_instruction(instruction, position, recipe_id, cur)

            recipe = await recipe_repository.get_recipe_by_id(recipe_id, user.id, cur)
            if recipe is None:
                msg = f'recipe with id {recipe_id} not found'
                raise ResourceNotFoundError(msg)

            return _recipe_from_row(recipe)

    async def update_recipe(self, recipe_id: UUID, recipe_update: RecipeUpdate, user: User):
        async with self.begin() as cur:
            current_recipe = await recipe_repository.get_recipe_by_id(recipe_id, user.id, cur)
            if current_recipe is None:
                msg = f'recipe with id {recipe_id} not found'
                raise ResourceNotFoundError(msg)
            current_recipe = _recipe_from_row(current_recipe)
            await recipe_repository.update_recipe(recipe_update, recipe_id, cur)

            current_instructions: set[UUID] = {instruction.id for instruction in current_recipe.instructions}
            new_instructions = {instruction.id for instruction in recipe_update.instructions if instruction.id is not None}

            deleted_instructions = current_instructions - new_instructions
            for deleted_instruction in deleted_instructions:
                await instruction_repository.delete_instruction(deleted_instruction, cur)

            for position, instruction in enumerate(recipe_update.instructions):
                if instruction.id is None:
                    await instruction_repository.insert_instruction(instruction.text, position, recipe_id, cur)
                else:
                    await instruction_repository.update_instruction(instruction.text, position, instruction.id, cur)

            current_ingredients: set[UUID] = {ingredient.id for ingredient in current_recipe.ingredients}
            new_ingredients = {ingredient.id for ingredient in recipe_update.ingredients if ingredient.id is not None}

            deleted_ingredients = current_ingredients - new_ingredients
            for deleted_ingredient in deleted_ingredients:
                await ingredient_repository.delete_ingredient(deleted_ingredient, cur)

            for position, ingredient in enumerate(recipe_update.ingredients):
                if ingredient.id is None:
                    await ingredient_repository.insert_ingredient(ingredient.text, position, recipe_id, cur)
                else:
                    await ingredient_repository.update_ingredient(ingredient.text, position, ingredient.id, cur)


def _recipe_from_row(row: DictRow) -> RecipeFull:
    cover_image_asset_url = f'/asset/{row["cover_image"]}' if row.get('cover_image') else None
    cover_thumbnail_asset_url = f'/asset/{row["cover_thumbnail"]}' if row.get('cover_thumbnail') else None
    return RecipeFull(
        id=row['id'],
        collection=row['collection'],
        created_by=row['created_by'],
        title=row['title'],
        slug=row['slug'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
        cook_time=row['cook_time'],
        prep_time=row['prep_time'],
        total_time=row['total_time'],
        recipe_yield=row['yield'],
        last_made=row['last_made'],
        instructions=row['instructions'] or [],
        ingredients=row['ingredients'] or [],
        liked=row['liked'],
        cover_image=cover_image_asset_url,
        cover_thumbnail=cover_thumbnail_asset_url,
        note=row['note']
    )


def _recipe_light_from_row(row: DictRow) -> RecipeLight:
    return RecipeLight(
        id=row['id'],
        collection=row['collection'],
        slug=row['slug'],
        title=row['title'],
        description=row['description'],
        liked=row['liked'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
    )
