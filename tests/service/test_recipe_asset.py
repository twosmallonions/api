import asyncio
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import uuid6

from tso_api.service import recipe_asset


def test_image_resizing():
    @patch('tso_api.repository.asset_repository.create_asset')
    async def run(mock1) -> None:
        conn = MagicMock()
        with (Path(__file__).parent / 'test.jpg').open('rb') as f:
            bytes_io = io.BytesIO(f.read())
        await recipe_asset.add_cover_image_to_recipe(uuid6.uuid7(), '123', bytes_io, 'test.jpg', conn)

    asyncio.run(run(), loop_factory=asyncio.new_event_loop)
