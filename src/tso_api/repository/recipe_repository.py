# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

import uuid6
from psycopg import AsyncCursor
from psycopg.rows import DictRow

from tso_api.models.recipe import RecipeCreate, RecipeUpdate
from tso_api.repository import NoneAfterInsertError, NoneAfterUpdateError


async def get_recipes_light_by_owner(cur: AsyncCursor[DictRow]):
    query = """SELECT
    r.id,
    r.collection_id,
    r.title,
    r.created_at,
    r.updated_at,
    r.liked,
    r.cover_thumbnail
FROM tso.recipe r"""
    return await (await cur.execute(query)).fetchall()


async def update_cover_image(
    recipe_id: UUID, asset_cover_id: UUID, asset_thumbnail_id: UUID, cur: AsyncCursor[DictRow]
):
    query = """UPDATE tso.recipe
    SET
        cover_image = %(cover_image)s,
        cover_thumbnail = %(cover_thumbnail)s
    WHERE
        id = %(id)s
    """
    res = await cur.execute(
        query, {'cover_image': asset_cover_id, 'cover_thumbnail': asset_thumbnail_id, 'id': recipe_id}
    )

    if res.rowcount == 0:
        msg = 'recipe'
        raise NoneAfterUpdateError(msg, recipe_id)


async def update_liked(liked: bool, recipe_id: UUID, cur: AsyncCursor[DictRow]):
    query = 'UPDATE recipes SET liked = %(liked)s WHERE owner = %(owner)s AND id = %(id)s'
    await cur.execute(query, {'liked': liked, 'id': recipe_id})


async def update_recipe(recipe: RecipeUpdate, recipe_id: UUID, cur: AsyncCursor[DictRow]):
    query = """UPDATE tso.recipe
    SET
        title = %(title)s,
        note = %(note)s,
        cook_time = %(cook_time)s,
        prep_time = %(prep_time)s,
        yield = %(yield)s,
        liked = %(liked)s
    WHERE
        id = %(id)s
    RETURNING *"""
    res = await (
        await cur.execute(
            query,
            {
                'title': recipe.title,
                'note': recipe.note,
                'cook_time': recipe.cook_time,
                'prep_time': recipe.prep_time,
                'yield': recipe.recipe_yield,
                'liked': recipe.liked,
                'id': recipe_id,
            },
        )
    ).fetchone()

    if res is None:
        msg = 'recipe'
        raise NoneAfterUpdateError(msg, recipe_id)

    return res


async def create_recipe(recipe: RecipeCreate, collection_id: UUID, created_by: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO tso.recipe
    (id, collection_id, created_by, title, cook_time, prep_time, yield, liked, note)
    VALUES (%(id)s, %(collection)s, %(created_by)s, %(title)s, %(cook_time)s, %(prep_time)s, %(yield)s, %(liked)s, %(note)s)
    RETURNING *"""

    recipe_id = uuid6.uuid7()
    res = await (
        await cur.execute(
            query,
            {
                'id': recipe_id,
                'collection': collection_id,
                'created_by': created_by,
                'title': recipe.title,
                'note': recipe.note,
                'cook_time': recipe.cook_time,
                'prep_time': recipe.prep_time,
                'yield': recipe.recipe_yield,
                'liked': recipe.liked,
            },
        )
    ).fetchone()

    if res is None:
        msg = 'recipe'
        raise NoneAfterInsertError(msg)

    return res


async def get_recipe_by_id(recipe_id: UUID, cur: AsyncCursor[DictRow]):
    query = """SELECT
        r.id,
        r.collection_id,
        r.title,
        r.created_at,
        r.updated_at,
        r.cook_time,
        r.prep_time,
        r.total_time,
        r.yield,
        r.last_made,
        r.liked,
        r.created_by,
        r.note,
        (
            SELECT
                array_agg(
                    json_build_object('text', ins.text, 'id', ins.id)
                    ORDER BY ins.position
                )
            FROM tso.instruction AS ins
            WHERE ins.recipe_id = r.id
        ) AS instructions,
        (
            SELECT
                array_agg(
                    json_build_object('text', ing.text, 'id', ing.id)
                    ORDER BY ing.position
                )
            FROM tso.ingredient AS ing
            WHERE ing.recipe_id = r.id
        ) AS ingredients,
        ( SELECT asset.id FROM tso.asset WHERE asset.id = r.cover_image ) AS cover_image,
        ( SELECT asset.id FROM tso.asset WHERE asset.id = r.cover_thumbnail ) AS cover_thumbnail
    FROM tso.recipe AS r
    WHERE r.id = %s"""
    return await (await cur.execute(query, (recipe_id,))).fetchone()
