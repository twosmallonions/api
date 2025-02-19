from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Instruction(BaseModel):
    text: str


class Ingredient(BaseModel):
    text: str


class Recipe(BaseModel):
    title: str
    description: str | None = None
    cook_time: int | None = None
    prep_time: int | None = None
    recipe_yield: str | None = None


class RecipeCreate(Recipe):
    instructions: list[str] = []
    ingredients: list[str] = []


class RecipeFull(Recipe):
    id: UUID
    owner: str
    slug: str
    created_at: datetime
    updated_at: datetime
    total_time: int | None = None
    last_made: datetime | None
    instructions: list[str] = []
    ingredients: list[str] = []
