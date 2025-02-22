from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InstructionBase(BaseModel):
    text: str


class IngredientBase(BaseModel):
    text: str


class InstructionUpdate(BaseModel):
    text: str
    id: UUID | None


class IngredientUpdate(BaseModel):
    text: str
    id: UUID | None


class Ingredient(IngredientBase):
    id: UUID


class Instruction(InstructionBase):
    id: UUID


class Recipe(BaseModel):
    title: str
    description: str | None = None
    cook_time: int | None = None
    prep_time: int | None = None
    recipe_yield: str | None = None
    liked: bool = False


class RecipeCreate(Recipe):
    instructions: list[str] = []
    ingredients: list[str] = []


class RecipeUpdate(Recipe):
    instructions: list[InstructionUpdate] = []
    ingredients: list[IngredientUpdate] = []


class RecipeFull(Recipe):
    id: UUID
    owner: str
    slug: str
    created_at: datetime
    updated_at: datetime
    total_time: int | None = None
    last_made: datetime | None
    instructions: list[Instruction] = []
    ingredients: list[Ingredient] = []
