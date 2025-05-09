# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

import uuid6
from psycopg import AsyncCursor
from psycopg.rows import DictRow


async def insert_ingredient(text: str, position: int, recipe_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO tso.ingredient (id, text, recipe_id, position)
    VALUES (%(id)s, %(text)s, %(recipe)s, %(position)s)"""

    ingredient_id = uuid6.uuid7()
    await cur.execute(query, {'id': ingredient_id, 'text': text, 'recipe': recipe_id, 'position': position})

    return ingredient_id


async def update_ingredient(text: str, position: int, ingredient_id: UUID, cur: AsyncCursor[DictRow]):
    query = """UPDATE tso.ingredient
    SET
        text = %(text)s,
        position = %(position)s
    WHERE
        id = %(id)s"""
    await cur.execute(query, {'text': text, 'position': position, 'id': ingredient_id})


async def delete_ingredient(ingredient_id: UUID, cur: AsyncCursor[DictRow]):
    query = 'DELETE FROM tso.ingredient WHERE id = %(id)s'
    await cur.execute(query, {'id': ingredient_id})
