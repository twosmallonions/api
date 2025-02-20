import uuid6
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from tso_api.routers.recipe import RecipeCreate, RecipeFull


class ResourceNotFoundError(Exception):
    msg: str = 'resource not found: {0}'
    resource: str

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(self.msg.format(resource))


SELECT_RECIPE_BY_SLUG = "SELECT * FROM recipes_full WHERE owner = %(owner)s AND slug = %(slug)s"

INSERT_RECIPE = """INSERT INTO recipes (id, owner, title, slug, description, cook_time, prep_time, yield)
VALUES (%(id)s, %(owner)s, %(title)s, %(slug)s, %(description)s, %(cook_time)s, %(prep_time)s, %(yield)s)
"""

INSERT_INSTRUCTION = """INSERT INTO instructions (id, text, recipe, position)
VALUES (%s, %s, %s, %s)
"""

INSERT_INGREDIENT = """INSERT INTO ingredients (id, text, recipe, position)
VALUES (%s, %s, %s, %s)
"""


async def create_recipe(recipe: RecipeCreate, owner: str, conn: AsyncConnection) -> RecipeFull:
    async with conn.transaction(), conn.cursor() as cur:
        recipe_id = uuid6.uuid7()
        _ = await cur.execute(
            INSERT_RECIPE,
            {
                'id': recipe_id,
                'owner': owner,
                'title': recipe.title,
                'slug': recipe.title.lower(),
                'description': recipe.description,
                'cook_time': recipe.cook_time,
                'prep_time': recipe.prep_time,
                'yield': recipe.recipe_yield,
            },
        )

        for query, text in (
            (sql.SQL(INSERT_INSTRUCTION), recipe.instructions),
            (sql.SQL(INSERT_INGREDIENT), recipe.ingredients),
        ):
            params_instructions = [(uuid6.uuid7(), text, recipe_id, index) for (index, text) in enumerate(text)]

            _ = await cur.executemany(query, params_instructions)

    return await get_recipe_by_slug(recipe.title.lower(), owner, conn)


async def get_recipe_by_slug(slug: str, owner: str, conn: AsyncConnection) -> RecipeFull:
    async with conn.cursor(row_factory=dict_row) as cur:
        row = await (await cur.execute(SELECT_RECIPE_BY_SLUG, {'owner': owner, 'slug': slug})).fetchone()

    if row is None:
        raise ResourceNotFoundError(slug)

    return RecipeFull(
        id=row['id'],
        owner=row['owner'],
        title=row['title'],
        slug=row['slug'],
        description=row['description'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
        cook_time=row['cook_time'],
        prep_time=row['prep_time'],
        total_time=row['total_time'],
        recipe_yield=row['yield'],
        last_made=row['last_made'],
        instructions=row['instructions'] or [],
        ingredients=row['ingredients'] or []
    )
