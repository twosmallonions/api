from pathlib import Path
import uuid6
from psycopg import AsyncConnection

from tso_api.models.asset import AssetBase
from tso_api.repository import asset_repository


async def test_create_asset(conn: AsyncConnection):
    asset_id = uuid6.uuid7()
    asset_base = AssetBase(id=asset_id, path=Path('/test/1'), size=623623, original_name='1')
    await asset_repository.create_asset(asset_base, conn)

    asset = await asset_repository.get_asset_by_id(asset_id, conn)

    assert asset.id == asset_id
    assert asset.path == asset_base.path
    assert asset.size == asset_base.size
    assert asset.original_name == asset_base.original_name
    assert asset.created_at
