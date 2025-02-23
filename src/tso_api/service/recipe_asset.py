import hashlib
import io
from pathlib import Path
from uuid import UUID

import uuid6
from PIL import Image
from PIL.Image import Resampling
from PIL.ImageFile import ImageFile
from psycopg import AsyncConnection

from tso_api.config import settings
from tso_api.models.asset import AssetBase
from tso_api.repository import asset_repository

RECIPE_COVER_IMAGE_RESOLUTION = (810, 540)
RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION = (324, 216)
RECIPE_COVER_IMAGE_FORMAT = 'webp'


async def add_cover_image_to_recipe(
    recipe_id: UUID, owner: str, file: io.BytesIO, original_filename: str, conn: AsyncConnection
):
    owner_hash = hashlib.sha1(owner.encode()).hexdigest()  # noqa: S324

    img = Image.open(file)
    cover_image_id = uuid6.uuid7()
    cover_image = resize_for_recipe_cover(img)
    cover_image_path = save_image(cover_image, owner_hash, recipe_id, cover_image_id, RECIPE_COVER_IMAGE_FORMAT)

    await create_asset(cover_image_path, original_filename, cover_image_id, conn)

    thumbnail_image_id = uuid6.uuid7()
    thumbnail_image = cover_image.copy()
    thumbnail_image.thumbnail(RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION)
    thumbnail_image_path = save_image(thumbnail_image, owner_hash, recipe_id, thumbnail_image_id, RECIPE_COVER_IMAGE_FORMAT)

    await create_asset(thumbnail_image_path, original_filename, thumbnail_image_id, conn)


def save_image(image: Image.Image, owner_hash: str, recipe_id: UUID, image_id: UUID, extension: str) -> Path:
    image_path = Path(settings.data_dir) / owner_hash / str(recipe_id) / f'{image_id}.{extension}'
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(image_path)

    return image_path


async def create_asset(
    image_path: Path, original_filename: str, image_id: UUID, conn: AsyncConnection
):
    asset = AssetBase(
        id=image_id,
        path=image_path,
        size=image_path.stat().st_size,
        original_name=original_filename,
    )
    await asset_repository.create_asset(asset, conn)


def resize_for_recipe_cover(image: ImageFile):
    (width, height) = image.size
    current_ratio = width / height
    (target_width, target_height) = RECIPE_COVER_IMAGE_RESOLUTION
    target_ratio = 1.5

    if height == target_height and width == target_width:
        return image

    if current_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * current_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / current_ratio)

    img = image.resize((new_width, new_height), Resampling.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img.crop((left, top, right, bottom))
