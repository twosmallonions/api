import uuid6
from psycopg import AsyncConnection

from tso_api.routers.recipe import RecipeCreate, RecipeFull


class ResourceNotFoundError(Exception):
    msg: str = 'resource not found: {0}'
    resource: str

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(self.msg.format(resource))


SELECT_RECIPE_BY_SLUG = """
SELECT * FROM recipes
WHERE owner = %(owner)s AND slug = %(slug)s
"""

INSERT_RECIPE = """
INSERT INTO recipes (id, owner, title, slug, description, cook_time, prep_time, yield)
VALUES (%(id)s, %(owner)s, %(title)s, %(slug)s, %(description)s, %(cook_time)s, %(prep_time)s, %(yield)s)
"""


async def create_recipe(recipe: RecipeCreate, owner: str, conn: AsyncConnection) -> RecipeFull:
    async with conn.cursor() as cur:
        _ = await cur.execute(
            INSERT_RECIPE,
            {
                'id': uuid6.uuid7(),
                'owner': owner,
                'title': recipe.title,
                'slug': recipe.title.lower(),
                'description': recipe.description,
                'cook_time': recipe.cook_time,
                'prep_time': recipe.prep_time,
                'yield': recipe.recipe_yield
            },
        )

    return await get_recipe_by_slug(recipe.title.lower(), owner, conn)


async def get_recipe_by_slug(slug: str, owner: str, conn: AsyncConnection) -> RecipeFull:
    async with conn.cursor() as cur:
        row = await (await cur.execute(SELECT_RECIPE_BY_SLUG, {'owner': owner, 'slug': slug})).fetchone()

    if row is None:
        raise ResourceNotFoundError(slug)

    return RecipeFull(
        id=row[0],
        owner=row[1],
        title=row[2],
        slug=row[3],
        description=row[4],
        created_at=row[5],
        updated_at=row[6],
        cook_time=row[7],
        prep_time=row[8],
        total_time=row[9],
        recipe_yield=row[10],
        last_made=row[11]
    )
