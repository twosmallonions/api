# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Dict
from uuid import UUID

from psycopg import AsyncCursor, sql
from psycopg.rows import DictRow
from uuid6 import uuid7

from tso_api.exceptions import NoneAfterInsertError, NoneAfterUpdateError


async def get_lists(cur: AsyncCursor[DictRow]) -> list[DictRow]:
    query = sql.SQL("""SELECT
   shopping_list.id,
   shopping_list.title,
   shopping_list.collection_id,
   shopping_list.created_at,
   shopping_list.updated_at,
    (
        SELECT COUNT(*) FROM tso.list_entry AS list_entry WHERE list_entry.list_id = shopping_list.id
    ) AS entries_total,
    (
        SELECT COUNT(*) FROM tso.list_entry AS list_entry WHERE list_entry.list_id = shopping_list.id AND list_entry.completed = false
    ) AS entries_not_completed
    FROM tso.shopping_list AS shopping_list
    ORDER BY shopping_list.title DESC
    """)

    res = await cur.execute(query)

    return await res.fetchall()


async def create_list(title: str, collection_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
    tso.shopping_list (id, title, collection_id)
    VALUES (%s, %s, %s) RETURNING *"""

    list_id = uuid7()

    res = await cur.execute(query, (list_id, title, collection_id))

    row = await res.fetchone()

    if row is None:
        msg = 'list'
        raise NoneAfterInsertError(msg)

    return row


async def update_list(title: str, list_id: UUID, collection_id: UUID, cur: AsyncCursor[DictRow]):
    query = """UPDATE
    tso.shopping_list
    SET title = %s
    WHERE id = %s AND collection_id = %s RETURNING *"""

    res = await cur.execute(query, (title, list_id, collection_id))

    row = await res.fetchone()

    if row is None:
        msg = 'list'
        raise NoneAfterUpdateError(msg, list_id)

    return row


async def add_entry_to_list(name: str, list_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
    tso.list_entry (id, name, list_id)
    VALUES (%s, %s, %s)
    RETURNING *
    """
    entry_id = uuid7()

    res = await cur.execute(query, (entry_id, name, list_id))

    row = await res.fetchone()

    if row is None:
        msg = 'list_entry'
        raise NoneAfterInsertError(msg)

    return row


async def set_list_entry_completed(entry_id: UUID, list_id: UUID, cur: AsyncCursor[DictRow]):
    await _update_entry_completed(True, entry_id, list_id, cur)  # noqa: FBT003


async def unset_list_entry_completed(entry_id: UUID, list_id: UUID, cur: AsyncCursor[DictRow]):
    await _update_entry_completed(False, entry_id, list_id, cur)  # noqa: FBT003


async def _update_entry_completed(completed: bool, entry_id: UUID, list_id: UUID, cur: AsyncCursor[DictRow]) -> None:
    completed_at = 'now()' if completed else 'null'
    query = sql.SQL("""UPDATE
    tso.list_entry
    SET completed_at = {completed_at}
    WHERE id = %s AND list_id = %s""").format(completed_at=sql.SQL(completed_at))

    res = await cur.execute(query, (entry_id, list_id))

    if res.rowcount == 0:
        msg = 'list_entry'
        raise NoneAfterUpdateError(msg, entry_id)


async def get_list(list_id: UUID, cur: AsyncCursor[DictRow]):
    query = """
WITH list_entries_data AS (
  SELECT
    e.list_id,
    COUNT(*) AS entries_count,
    array_agg(
      json_build_object(
        'id', e.id,
        'name', e.name,
        'note', e.note,
        'created_at', e.created_at,
        'updated_at', e.updated_at,
        'completed', e.completed,
        'completed_at', e.completed_at
      ) ORDER BY e.created_at
    ) AS entries_array
  FROM tso.list_entry e
  WHERE e.list_id = %(list_id)s
  GROUP BY e.list_id
)
SELECT
  l.id,
  l.collection_id,
  l.title,
  l.created_at,
  l.updated_at,
  COALESCE(led.entries_array, '{}') AS entries,
  COALESCE(led.entries_count, 0) AS num_entries
FROM tso.shopping_list l
LEFT JOIN list_entries_data led ON l.id = led.list_id
WHERE l.id = %(list_id)s;
"""

    res = await cur.execute(query, {'list_id': list_id})

    row = await res.fetchone()

    if row is None:
        msg = 'shopping list'
        raise NoneAfterInsertError(msg)

    return row
