# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any
from uuid import UUID

from psycopg import AsyncCursor
from psycopg.rows import DictRow
from uuid6 import uuid7

from tso_api.repository import NoneAfterInsertError, NoneAfterUpdateError

INSERT_SHOPPING_LIST_QUERY = """INSERT INTO
shopping_lists
    (id, owner, title)
VALUES (%(id)s, %(owner)s, %(title)s)"""

INSERT_SHOPPING_LIST_ENTRY_QUERY = """INSERT INTO
list_entries
    (id, name, note, shopping_list)
VALUES (%(id)s, %(name)s, %(note)s, %(shopping_list)s)"""

SELECT_SHOPPING_LISTS = """SELECT
l.id, l.owner, l.title, l.created_at, l.updated_at
FROM shopping_lists l
WHERE l.id = %(id)s AND l.owner = %(owner)s
"""

SELECT_SHOPPING_LISTS_WITH_ENTRIES = """SELECT
* FROM shopping_lists_with_entries led
WHERE led.id = %(id)s AND led.owner = %(owner)s
"""

UPDATE_ENTRY_SET_COMPLETED = """UPDATE
list_entries SET completed = true
WHERE id = %(id)s AND owner = %(owner)s
"""


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


async def _update_entry_completed(completed: bool, entry_id: UUID, list_id: UUID, cur: AsyncCursor[DictRow]) -> None:  # noqa: FBT001
    query = """UPDATE
    tso.list_entry
    SET completed = %s
    WHERE id = %s AND list_id = %s"""

    res = await cur.execute(query, (completed, entry_id, list_id))

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
