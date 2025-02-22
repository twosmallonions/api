import hashlib
import io
from pathlib import Path
from uuid import UUID

from PIL import Image
from PIL.ImageFile import ImageFile
from psycopg import AsyncConnection
import uuid6

from tso_api.config import settings

RECIPE_COVER_IMAGE_RESOLUTION = (810, 540)
RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION = (324, 216)

async def add_cover_image_to_recipe(recipe_id: UUID, owner: str, file: io.BytesIO, db: AsyncConnection):
    owner_hash = hashlib.sha1(owner.encode()).hexdigest()  # noqa: S324

    img = Image.open(file)
    cover_image_id = uuid6.uuid7()
    cover_image = resize_for_recipe_cover(img)
    cover_image_path = Path(settings.data_dir) / owner_hash / str(recipe_id) / f'{cover_image_id}.webp'
    cover_image.save(cover_image_path)

    thumbnail_image_id = uuid6.uuid7()
    thumbnail_image = cover_image.copy()
    thumbnail_image.thumbnail(RECIPE_COVER_IMAGE_THUMBNAIL_RESOLUTION)
    thumbnail_image_path = Path(settings.data_dir) / owner_hash / str(recipe_id) / f'{thumbnail_image_id}.webp'
    thumbnail_image.save(thumbnail_image_path)
    # persist to database

    # update recipe
    # ???
    # profit


def resize_for_recipe_cover(image: ImageFile):
    return image.resize(RECIPE_COVER_IMAGE_RESOLUTION)
