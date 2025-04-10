from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from tso_api.models.asset import Asset, AssetBase
from tso_api.service.base_service import ResourceNotFoundError

INSERT_ASSET = """INSERT INTO
assets (id, path, size, original_name, owner)
VALUES (%(id)s, %(path)s, %(size)s, %(original_name)s, %(owner)s)"""

SELECT_ASSET = 'SELECT id, path, size, original_name, created_at FROM assets WHERE id = %s AND owner = %s'


async def create_asset(asset: AssetBase, owner: str, conn: AsyncConnection) -> Asset:
    async with conn.transaction(), conn.cursor() as cur:
        res = await cur.execute(
            INSERT_ASSET + ' RETURNING created_at',
            {'id': asset.id, 'path': str(asset.path), 'size': asset.size, 'original_name': asset.original_name, 'owner': owner},
        )
        row = await res.fetchone()
        if row is None:
            msg = 'asset'
            raise ResourceNotFoundError(msg)

    return Asset(created_at=row[0], **asset.model_dump())


async def get_asset_by_id(asset_id: UUID, owner: str, conn: AsyncConnection) -> Asset:
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        res = await cur.execute(SELECT_ASSET, (asset_id, owner))

        row = await res.fetchone()
        if row is None:
            msg = f'asset: {asset_id}'
            raise ResourceNotFoundError(msg)

    return Asset(id=row['id'], path=row['path'], size=row['size'], original_name=row['original_name'], created_at=row['created_at'])
