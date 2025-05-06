# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from tso_api.models.base import Timestamps, TSOBase


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
    note: str = ''
    cook_time: int | None = None
    prep_time: int | None = None
    recipe_yield: str | None = None
    liked: bool = False
    original_url: str | None = None


class RecipeCreate(Recipe):
    instructions: list[str] = []
    ingredients: list[str] = []


class RecipeUpdate(Recipe):
    instructions: list[InstructionUpdate] = []
    ingredients: list[IngredientUpdate] = []


class RecipeFull(Recipe, Timestamps):
    id: UUID
    total_time: int | None = None
    last_made: datetime | None
    instructions: list[Instruction] = []
    ingredients: list[Ingredient] = []
    cover_image: UUID | None = None
    cover_thumbnail: UUID | None = None
    collection: UUID
    created_by: UUID


class RecipeLight(Timestamps):
    id: UUID
    collection: UUID
    title: str
    description: str | None
    liked: bool
    cover_thumbnail: UUID | None


class ImportRecipe(TSOBase):
    url: HttpUrl
