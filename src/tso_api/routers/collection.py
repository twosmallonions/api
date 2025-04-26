# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


from fastapi import APIRouter

from tso_api.dependency import CollectionServiceDep, GetUser
from tso_api.models.collection import CollectionCreate

router = APIRouter(prefix='/api/collection')


@router.get('/')
async def get_collections_for_user(user: GetUser, collection_service: CollectionServiceDep):
    return await collection_service.get_collections_for_user(user)


@router.post('/')
async def create_collection(
    collection_create: CollectionCreate, user: GetUser, collection_service: CollectionServiceDep
):
    return await collection_service.new_collection(collection_create, user)
