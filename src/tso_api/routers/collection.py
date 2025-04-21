# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

from fastapi import APIRouter

from tso_api.dependency import GetUser
from tso_api.models.collection import CollectionCreate
from tso_api.models.recipe import RecipeCreate, RecipeFull
from tso_api.service import collection_service, recipe_service

router = APIRouter(prefix='/api/collection')


@router.post('/')
async def create_collection(collection_create: CollectionCreate, user: GetUser):
    return await collection_service.new_collection(collection_create, user)


@router.post('/{collection_id}/recipe')
async def create_recipe(recipe_create: RecipeCreate, user: GetUser, collection_id: UUID) -> RecipeFull:
    return await recipe_service.create(recipe_create, user, collection_id)
