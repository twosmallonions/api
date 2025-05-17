# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import base64
import datetime
from typing import Any
from uuid import UUID

import uuid6
from psycopg import AsyncCursor, sql
from psycopg.rows import DictRow
from pydantic import BaseModel, ConfigDict, Field

from tso_api.exceptions import CursorPaginationError, NoneAfterInsertError, NoneAfterUpdateError
from tso_api.models.query_params import RecipeSortField, SortOrder
from tso_api.models.recipe import RecipeCreate, RecipeUpdate


class CursorStructure(BaseModel):
    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)
    last_value: str | datetime.datetime | int = Field(alias='l')
    sort_order: SortOrder = Field(alias='o')
    sort_field: str = Field(alias='f')
    last_id: UUID = Field(alias='i')


def _decode_cursor(cursor: str) -> CursorStructure:
    decoded_cursor = base64.urlsafe_b64decode(cursor).decode('utf-8')
    return CursorStructure.model_validate_json(decoded_cursor)


def _verify_cursor_struct(cursor_struct: CursorStructure, sort_field: RecipeSortField, sort_order: SortOrder):
    if cursor_struct.sort_order != sort_order:
        msg = "sort_order doesn't match"
        raise CursorPaginationError(msg)

    if cursor_struct.sort_field != sort_field:
        msg = "sort_field doesn't match"
        raise CursorPaginationError(msg)


def _build_cursor_where_query(cursor_struct: CursorStructure) -> sql.Composed:
    sort_order_symbol = sql.SQL('<') if cursor_struct.sort_order == SortOrder.DESC else sql.SQL('>')

    return sql.SQL('(r.{sort_field}, r.id) {sort_order_symbol} (%(cursor_sort_value)s, %(cursor_sort_id)s)').format(
        sort_field=sql.Identifier(cursor_struct.sort_field), sort_order_symbol=sort_order_symbol
    )


class WhereClause:
    def __init__(self) -> None:
        self.where_clause: list[sql.Composable] = []
        self.params: dict[str, Any]

    def add_clause(self, sql: sql.Composed, params: dict[str, Any]):
        self.where_clause.append(sql)
        self.params |= params

    def build(self):
        if len(self.where_clause) != 0:
            self.where_clause.insert(0, sql.SQL('WHERE '))

        return self.where_clause


async def get_recipes_light_by_owner(
    cur: AsyncCursor[DictRow],
    limit: int,
    sort_field: RecipeSortField = RecipeSortField.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    cursor: str | None = None,
) -> tuple[list[DictRow], str | None]:
    where_clause = WhereClause()
    if cursor:
        cursor_struct = _decode_cursor(cursor)
        _verify_cursor_struct(cursor_struct, sort_field, sort_order)

        cursor_where_clause = _build_cursor_where_query(cursor_struct)
        cursor_where_clause_params = {
            'cursor_sort_value': cursor_struct.last_value,
            'cursor_sort_id': cursor_struct.last_id,
        }
        where_clause.add_clause(cursor_where_clause, cursor_where_clause_params)

    sort_order_sql = sql.SQL('DESC') if sort_order == SortOrder.DESC else sql.SQL('ASC')
    query = sql.SQL("""SELECT
    r.id,
    r.collection_id,
    r.title,
    r.created_at,
    r.updated_at,
    r.liked,
    r.cover_thumbnail
FROM tso.recipe r
{where_clause}
ORDER BY r.{sort_field} {sort_order}, r.id {sort_order}
LIMIT %(limit)s""").format(
        sort_field=sql.Identifier(sort_field),
        sort_order=sort_order_sql,
        where_clause=sql.Composed(where_clause.build()),
    )
    params = {'limit': limit + 1} | where_clause.params
    res = await (await cur.execute(query, params)).fetchall()

    if len(res) != limit + 1:
        return (res, None)

    cursor_value = res[limit - 1]

    new_cursor_value = cursor_value.get(sort_field)
    if new_cursor_value is None:
        msg = 'new_cursor_value is none'
        raise CursorPaginationError(msg)

    new_cursor_id = cursor_value.get('id')

    if new_cursor_id is None:
        msg = 'new_cursor_id is None'
        raise CursorPaginationError(msg)

    new_cursor_struct = CursorStructure.model_validate(
        {'last_value': new_cursor_value, 'sort_order': sort_order, 'sort_field': sort_field, 'last_id': new_cursor_id}
    )

    new_cursor = base64.urlsafe_b64encode(new_cursor_struct.model_dump_json(by_alias=True).encode('utf-8')).decode(
        'utf-8'
    )

    return res[:-1], new_cursor


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
        liked = %(liked)s,
        original_url = %(original_url)s
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
                'original_url': recipe.original_url,
            },
        )
    ).fetchone()

    if res is None:
        msg = 'recipe'
        raise NoneAfterUpdateError(msg, recipe_id)

    return res


async def create_recipe(recipe: RecipeCreate, collection_id: UUID, created_by: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO tso.recipe
    (id, collection_id, created_by, title, cook_time, prep_time, yield, liked, note, original_url)
    VALUES (%(id)s, %(collection)s, %(created_by)s, %(title)s, %(cook_time)s, %(prep_time)s, %(yield)s, %(liked)s, %(note)s, %(original_url)s)
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
                'original_url': recipe.original_url,
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
        r.original_url,
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
