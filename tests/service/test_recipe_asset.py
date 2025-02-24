import asyncio
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import uuid6

from tso_api.service import recipe_asset


async def test_image_resizing():
    with patch('tso_api.repository.asset_repository.create_asset'):
        conn = MagicMock()
        with (Path(__file__).parent / 'test.jpg').open('rb') as f:
            await recipe_asset.add_cover_image_to_recipe(uuid6.uuid7(), '123', f, 'test.jpg', conn)
