# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only


from uuid import UUID
from fastapi import APIRouter

from tso_api.dependency import CollectionServiceDep, GetUser
from tso_api.models.collection import CollectionCreate, CollectionFull, CollectionWithUsers
from tso_api.models.user import AddUserToCollection

router = APIRouter(prefix='/api/collection')


@router.get('/')
async def get_collections_for_user(user: GetUser, collection_service: CollectionServiceDep) -> list[CollectionFull]:
    return await collection_service.get_collections_for_user(user)


@router.get('/')
async def get_collections_for_user_with_users(user: GetUser, collection_service: CollectionServiceDep) -> list[CollectionWithUsers]:
    return await collection_service.get_collections_for_user_with_members(user)


@router.post('/')
async def create_collection(
    collection_create: CollectionCreate, user: GetUser, collection_service: CollectionServiceDep
) -> CollectionFull:
    return await collection_service.new_collection(collection_create, user)


@router.post('/{collection_id}')
async def add_user_to_collection(
    user: GetUser, collection_id: UUID, user_to_add: AddUserToCollection, collection_service: CollectionServiceDep
) -> list[CollectionWithUsers]:
    return []
