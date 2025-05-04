# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

from psycopg import AsyncCursor
from psycopg.rows import DictRow

from tso_api.exceptions import NoneAfterInsertError
from tso_api.models.asset import AssetBase


async def create_asset(asset: AssetBase, collection_id: UUID, cur: AsyncCursor[DictRow]):
    query = """INSERT INTO
    tso.asset (id, path, size, original_name, collection_id)
    VALUES (%(id)s, %(path)s, %(size)s, %(original_name)s, %(collection_id)s)
    RETURNING *"""
    res = await cur.execute(
        query,
        {
            'id': asset.id,
            'path': str(asset.path),
            'size': asset.size,
            'original_name': asset.original_name,
            'collection_id': collection_id,
        },
    )
    row = await res.fetchone()
    if row is None:
        msg = 'asset'
        raise NoneAfterInsertError(msg)

    return row


async def get_asset_by_id(asset_id: UUID, collection_id: UUID, cur: AsyncCursor[DictRow]):
    query = 'SELECT id, path, size, original_name, created_at FROM tso.asset WHERE id = %s AND collection_id = %s'
    res = await cur.execute(query, (asset_id, collection_id))

    return await res.fetchone()
