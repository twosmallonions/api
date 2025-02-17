from psycopg_pool import AsyncConnectionPool
import uuid6

from ..routers.recipe import RecipeCreate, RecipeFull

SELECT_RECIPE_BY_SLUG = """
SELECT * FROM recipes
WHERE owner = %(owner)s AND slug = %(slug)s
"""

INSERT_RECIPE = """
INSERT INTO recipes (id, owner, title, slug, description)
VALUES (%(id)s, %(owner)s, %(title)s, %(slug)s, %(description)s)
"""

class RecipeRepository():
    pool: AsyncConnectionPool
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool = pool
    
    async def get_recipe_by_slug(self, slug: str, owner: str) -> RecipeFull:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                row = await (await cur.execute(SELECT_RECIPE_BY_SLUG, {'owner': owner, 'slug': slug})).fetchone()

        if row is None:
            raise Exception('not found')
        
        return RecipeFull(id=row[0], owner=row[1], title=row[2], slug=row[3], description=row[4], created_at=row[5], updated_at=row[6])
    
    async def create_recipe(self, recipe: RecipeCreate, owner: str) -> RecipeFull:
        async with self.pool.connection(timeout=1) as conn:
            async with conn.cursor() as cur:
                await cur.execute(INSERT_RECIPE, {
                    'id': uuid6.uuid7(),
                    'owner': owner,
                    'title': recipe.title,
                    'slug': recipe.title.lower(),
                    'description': recipe.description
                    }
                )
        recipe_full = await self.get_recipe_by_slug(recipe.title.lower(), owner)

        return recipe_full
