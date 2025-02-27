import asyncio
import hashlib
from pathlib import Path
from typing import IO
from uuid import UUID

import uuid6
from PIL import Image
from PIL.Image import Resampling
from PIL.ImageFile import ImageFile
from psycopg import AsyncConnection

from tso_api.models.asset import AssetBase
from tso_api.repository import asset_repository

RECIPE_COVER_IMAGE_RESOLUTION = (810, 540)
RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION = (324, 216)
RECIPE_COVER_IMAGE_FORMAT = 'webp'


async def add_cover_image_to_recipe(
    recipe_id: UUID, owner: str, file: IO[bytes] | Path, original_filename: str | None, conn: AsyncConnection
):
    owner_hash = hashlib.sha1(owner.encode()).hexdigest()  # noqa: S324
    loop = asyncio.get_running_loop()

    img = Image.open(file)
    cover_image_id = uuid6.uuid7()
    cover_image = await loop.run_in_executor(None, resize_for_recipe_cover, img)
    cover_image_path = await loop.run_in_executor(
        None, save_image, cover_image, owner_hash, recipe_id, cover_image_id, RECIPE_COVER_IMAGE_FORMAT
    )

    await create_asset(cover_image_path, original_filename, cover_image_id, owner, conn)

    thumbnail_image_id = uuid6.uuid7()
    thumbnail_image = await loop.run_in_executor(None, make_thumbnail, cover_image)
    thumbnail_image_path = await loop.run_in_executor(
        None, save_image, thumbnail_image, owner_hash, recipe_id, thumbnail_image_id, RECIPE_COVER_IMAGE_FORMAT
    )

    await create_asset(thumbnail_image_path, original_filename, thumbnail_image_id, owner, conn)


def make_thumbnail(img: ImageFile | Image.Image):
    img_copy = img.copy()
    img_copy.thumbnail(RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION)
    return img_copy


def save_image(image: Image.Image, owner_hash: str, recipe_id: UUID, image_id: UUID, extension: str) -> Path:
    image_path = Path(owner_hash) / str(recipe_id) / f'{image_id}.{extension}'
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(image_path)

    return image_path


async def create_asset(
    image_path: Path, original_filename: str | None, image_id: UUID, owner: str, conn: AsyncConnection
):
    asset = AssetBase(id=image_id, path=image_path, size=image_path.stat().st_size, original_name=original_filename)
    await asset_repository.create_asset(asset, owner, conn)


def resize_for_recipe_cover(image: ImageFile):
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
