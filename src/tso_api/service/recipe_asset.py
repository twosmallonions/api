# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

import uuid6
from PIL import Image
from PIL.Image import Resampling
from PIL.ImageFile import ImageFile
from psycopg import AsyncCursor
from psycopg.rows import DictRow

from tso_api.config import settings
from tso_api.exceptions import ResourceNotFoundError
from tso_api.models.asset import Asset, AssetBase
from tso_api.models.user import User
from tso_api.repository import asset_repository, recipe_repository
from tso_api.service.base_service import BaseService

RECIPE_COVER_IMAGE_RESOLUTION = (800, 800)
RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION = (400, 400)
RECIPE_COVER_IMAGE_FORMAT = 'webp'
RECIPE_COVER_IMAGE_MIME_TYPE = 'image/webp'


class RecipeAssetService(BaseService):
    # TODO: make file be something more generic
    async def add_cover_image_to_recipe(
        self, recipe_id: UUID, collection_id: UUID, user: User, file: BinaryIO, filename: str | None
    ):
        loop = asyncio.get_running_loop()
        img = Image.open(file)
        cover_image_id = uuid6.uuid7()
        cover_image = await loop.run_in_executor(None, _resize_for_recipe_cover, img)
        cover_image_path = await loop.run_in_executor(
            None, _save_image, cover_image, user.id, recipe_id, cover_image_id, RECIPE_COVER_IMAGE_FORMAT
        )
        async with self._begin(user.id) as cur:
            await _create_asset(cover_image_path, filename, cover_image_id, collection_id, cur)

            thumbnail_image_id = uuid6.uuid7()
            thumbnail_image = await loop.run_in_executor(None, _make_thumbnail, cover_image)
            thumbnail_image_path = await loop.run_in_executor(
                None, _save_image, thumbnail_image, user.id, recipe_id, thumbnail_image_id, RECIPE_COVER_IMAGE_FORMAT
            )

            await _create_asset(thumbnail_image_path, filename, thumbnail_image_id, collection_id, cur)

            await recipe_repository.update_cover_image(recipe_id, cover_image_id, thumbnail_image_id, cur)

    async def get_asset(self, collection_id: UUID, asset_id: UUID, user: User):
        async with self._begin(user.id) as cur:
            row = await asset_repository.get_asset_by_id(asset_id, collection_id, cur)
            if row is None:
                raise ResourceNotFoundError(str(asset_id))

        return _asset_from_row(row)


def _asset_from_row(row: DictRow) -> Asset:
    return Asset.model_validate(row)


async def _create_asset(
    image_path: Path, original_filename: str | None, image_id: UUID, collection_id: UUID, cur: AsyncCursor[DictRow]
):
    asset = AssetBase(id=image_id, path=image_path, size=image_path.stat().st_size, original_name=original_filename)
    await asset_repository.create_asset(asset, collection_id, cur)


def _make_thumbnail(img: ImageFile | Image.Image):
    img_copy = img.copy()
    img_copy.thumbnail(RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION)
    return img_copy


def _save_image(image: Image.Image, user_id: UUID, recipe_id: UUID, image_id: UUID, extension: str) -> Path:
    image_path = Path(settings.data_dir / str(user_id)) / str(recipe_id) / f'{image_id}.{extension}'
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(image_path)

    return image_path


def _resize_for_recipe_cover(image: ImageFile):
    (width, height) = image.size
    current_ratio = width / height
    (target_width, target_height) = RECIPE_COVER_IMAGE_RESOLUTION
    target_ratio = target_width / target_height

    if height == target_height and width == target_width:
        return image

    if current_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * current_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / current_ratio)

    img = image.resize((new_width, new_height), Resampling.LANCZOS)  # pyright: ignore[reportUnknownMemberType]

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img.crop((left, top, right, bottom))
