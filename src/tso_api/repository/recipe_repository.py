from uuid import UUID

import uuid6
from psycopg import AsyncConnection, AsyncCursor, sql
from psycopg.rows import DictRow, dict_row

from tso_api.models.recipe import RecipeCreate, RecipeFull, RecipeLight, RecipeUpdate
from tso_api.models.user import User


class ResourceNotFoundError(Exception):
    msg: str = 'resource not found: {0}'
    resource: str

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(self.msg.format(resource))


SELECT_RECIPE_BY_SLUG = """SELECT r.* FROM recipes_full r
INNER JOIN collections c
ON c.id = r.collection
LEFT JOIN collection_members cm
ON cm.collection = r.collection AND cm.user = %(user_id)s
WHERE r.slug = %(slug)s AND (c.owner = %(user_id)s OR cm.user IS NOT NULL)"""

SELECT_RECIPE_BY_ID = """SELECT r.* FROM recipes_full r
INNER JOIN collections c
ON c.id = r.collection
LEFT JOIN collection_members cm
ON cm.collection = r.collection AND cm.user = %(user_id)s
WHERE r.id = %(id)s AND (c.owner = %(user_id)s OR cm.user IS NOT NULL)"""
SELECT_RECIPE_LIGHT_BY_OWNER = 'SELECT * FROM recipes_lite WHERE %(user_id) IN users'

UPDATE_RECIPE_LIKED = 'UPDATE recipes SET liked = %(liked)s WHERE owner = %(owner)s AND id = %(id)s'

UPDATE_RECIPE_COVER_IMAGE = """UPDATE recipes
SET
    cover_image = %(cover_image)s,
    cover_thumbnail = %(cover_thumbnail)s
WHERE
    owner = %(owner)s AND id = %(id)s
"""

INSERT_RECIPE = """INSERT INTO recipes
(id, collection, created_by, title, slug, cook_time, prep_time, yield, liked)
VALUES (%(id)s, %(collection)s, %(created_by)s, %(title)s, %(slug)s, %(cook_time)s, %(prep_time)s, %(yield)s, %(liked)s)"""

UPDATE_RECIPE = """UPDATE recipes
SET
    title = %(title)s,
    slug = %(slug)s,
    description = %(description)s,
    cook_time = %(cook_time)s,
    prep_time = %(prep_time)s,
    yield = %(yield)s,
    liked = %(liked)s,
    updated_at = now()
WHERE
    owner = %(owner)s AND id = %(id)s"""

INSERT_INSTRUCTION = """INSERT INTO instructions (id, text, recipe, position)
VALUES (%(id)s, %(text)s, %(recipe)s, %(position)s)"""

UPDATE_INSTRUCTION = """UPDATE instructions
SET
   text = %(text)s,
   position = %(position)s
WHERE
    id = %(id)s"""

INSERT_INGREDIENT = """INSERT INTO ingredients (id, text, recipe, position)
VALUES (%(id)s, %(text)s, %(recipe)s, %(position)s)"""

UPDATE_INGREDIENT = """UPDATE ingredients
SET
   text = %(text)s,
   position = %(position)s
WHERE
    id = %(id)s"""

DELETE_INGREDIENT = 'DELETE FROM ingredients WHERE id = %(id)s'
DELETE_INSTRUCTION = 'DELETE FROM instructions WHERE id = %(id)s'


async def get_recipes_light_by_owner(owner: str, conn: AsyncConnection):
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        res = await (await cur.execute(SELECT_RECIPE_LIGHT_BY_OWNER, (owner,))).fetchall()

    return [__recipe_light_from_row(recipe) for recipe in res]


def __recipe_light_from_row(row: DictRow) -> RecipeLight:
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


async def update_cover_image(
    recipe_id: UUID, owner: str, asset_cover_id: UUID, asset_thumbnail_id: UUID, conn: AsyncConnection
):
    async with conn.transaction(), conn.cursor() as cur:
        await cur.execute(
            UPDATE_RECIPE_COVER_IMAGE,
            {'cover_image': asset_cover_id, 'cover_thumbnail': asset_thumbnail_id, 'id': recipe_id, 'owner': owner},
        )


async def update_liked(liked: bool, recipe_id: UUID, owner: str, conn: AsyncConnection) -> bool:
    async with conn.transaction(), conn.cursor() as cur:
        await cur.execute(UPDATE_RECIPE_LIKED, {'liked': liked, 'owner': owner, 'id': recipe_id})

        return liked


async def update_recipe(recipe: RecipeUpdate, owner: str, recipe_id: UUID, conn: AsyncConnection) -> RecipeFull:
    async with conn.transaction(), conn.cursor() as cur:
        current_recipe = await get_recipe_by_id(recipe_id, owner, conn)
        await cur.execute(
            UPDATE_RECIPE,
            {
                'title': recipe.title,
                'slug': recipe.title.lower(),
                'description': recipe.description,
                'cook_time': recipe.cook_time,
                'prep_time': recipe.prep_time,
                'yield': recipe.recipe_yield,
                'liked': recipe.liked,
                'owner': owner,
                'id': recipe_id,
            },
        )

        current_instructions = {a.id for a in current_recipe.instructions}
        new_instructions = {a.id for a in recipe.instructions if a.id is not None}

        deleted_instructions = current_instructions - new_instructions
        for deleted_instruction in deleted_instructions:
            await cur.execute(DELETE_INSTRUCTION, {'id': deleted_instruction})

        for position, instruction in enumerate(recipe.instructions):
            if instruction.id is None:
                await insert_instruction(instruction.text, recipe_id, position, cur)
            else:
                await cur.execute(
                    UPDATE_INSTRUCTION,
                    {'text': instruction.text, 'position': position, 'owner': owner, 'id': instruction.id},
                )

        current_ingredients_set = {a.id for a in current_recipe.ingredients}
        new_ingredients_set = {a.id for a in recipe.ingredients if a.id is not None}

        deleted_ingredients = current_ingredients_set - new_ingredients_set
        for deleted_ingredient in deleted_ingredients:
            await cur.execute(DELETE_INGREDIENT, {'id': deleted_ingredient})

        for position, ingredient in enumerate(recipe.ingredients):
            if ingredient.id is None:
                await insert_ingredient(ingredient.text, recipe_id, position, cur)
            else:
                await cur.execute(
                    UPDATE_INGREDIENT,
                    {'text': ingredient.text, 'position': position, 'owner': owner, 'id': ingredient.id},
                )
    return await get_recipe_by_id(recipe_id, owner, conn)


async def insert_ingredient(text: str, recipe_id: UUID, position: int, cur: AsyncCursor):
    ingredient_id = uuid6.uuid7()
    await cur.execute(INSERT_INGREDIENT, {'id': ingredient_id, 'text': text, 'recipe': recipe_id, 'position': position})

    return ingredient_id


async def insert_instruction(text: str, recipe_id: UUID, position: int, cur: AsyncCursor):
    ingredient_id = uuid6.uuid7()
    await cur.execute(
        INSERT_INSTRUCTION, {'id': ingredient_id, 'text': text, 'recipe': recipe_id, 'position': position}
    )

    return ingredient_id


async def create_recipe(recipe: RecipeCreate, created_by: User, collection: UUID, conn: AsyncConnection) -> RecipeFull:
    async with conn.transaction(), conn.cursor() as cur:
        recipe_id = uuid6.uuid7()
        _ = await cur.execute(
            INSERT_RECIPE,
            {
                'id': recipe_id,
                'collection': collection,
                'created_by': created_by.id,
                'title': recipe.title,
                'slug': recipe.title.lower(),
                'description': recipe.description,
                'cook_time': recipe.cook_time,
                'prep_time': recipe.prep_time,
                'yield': recipe.recipe_yield,
                'liked': recipe.liked,
            },
        )

        for query, text in (
            (sql.SQL(INSERT_INSTRUCTION), recipe.instructions),
            (sql.SQL(INSERT_INGREDIENT), recipe.ingredients),
        ):
            params_instructions = [
                {'id': uuid6.uuid7(), 'text': text, 'recipe': recipe_id, 'position': index}
                for (index, text) in enumerate(text)
            ]

            _ = await cur.executemany(query, params_instructions)

    return await get_recipe_by_slug(recipe.title.lower(), created_by, conn)


def __recipe_from_row(row: DictRow) -> RecipeFull:
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
    )


async def get_recipe_by_id(recipe_id: UUID, user: User, conn: AsyncConnection) -> RecipeFull:
    async with conn.cursor(row_factory=dict_row) as cur:
        row = await (await cur.execute(SELECT_RECIPE_BY_ID, {'user_id': user.id, 'id': recipe_id})).fetchone()

    if row is None:
        raise ResourceNotFoundError(str(recipe_id))

    return __recipe_from_row(row)


async def get_recipe_by_slug(slug: str, user: User, conn: AsyncConnection) -> RecipeFull:
    async with conn.cursor(row_factory=dict_row) as cur:
        row = await (await cur.execute(SELECT_RECIPE_BY_SLUG, {'user_id': user.id, 'slug': slug})).fetchone()

    if row is None:
        raise ResourceNotFoundError(slug)

    return __recipe_from_row(row)
