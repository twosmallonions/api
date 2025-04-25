# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from uuid import UUID

from pydantic import Field

from tso_api.models.base import TSOBase, Timestamps


class InstructionBase(TSOBase):
    text: str


class IngredientBase(TSOBase):
    text: str


class InstructionUpdate(TSOBase):
    text: str
    id: UUID | None


class IngredientUpdate(TSOBase):
    text: str
    id: UUID | None


class Ingredient(IngredientBase):
    id: UUID


class Instruction(InstructionBase):
    id: UUID


class Recipe(TSOBase):
    title: str
    note: str = ""
    cook_time: int | None = None
    prep_time: int | None = None
    recipe_yield: str | None = None
    liked: bool = False


class RecipeCreate(Recipe):
    instructions: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)


class RecipeUpdate(Recipe):
    instructions: list[InstructionUpdate] = Field(default_factory=list)
    ingredients: list[IngredientUpdate] = Field(default_factory=list)


class RecipeFull(Recipe, Timestamps):
    id: UUID
    total_time: int | None = None
    last_made: datetime | None
    instructions: list[Instruction] = Field(default_factory=list)
    ingredients: list[Ingredient] = Field(default_factory=list)
    cover_image: str | None = None
    cover_thumbnail: str | None = None
    collection: UUID
    created_by: UUID


class RecipeLight(Timestamps):
    id: UUID
    collection: UUID
    title: str
    description: str | None
    liked: bool
    cover_thumbnail: UUID | None
