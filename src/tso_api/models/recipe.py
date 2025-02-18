from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Recipe(BaseModel):
    title: str
    description: str | None = None
    cook_time: int | None = None
    prep_time: int | None = None
    recipe_yield: str | None = None


class RecipeCreate(Recipe):
    pass


class RecipeFull(Recipe):
    id: UUID
    owner: str
    slug: str
    created_at: datetime
    updated_at: datetime
    total_time: int | None = None
    last_made: datetime | None
