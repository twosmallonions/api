# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID

from fastapi import APIRouter, Response, status

from tso_api.dependency import GetUser, ShoppingListServiceDep
from tso_api.models.shopping_list import (
    ShoppingListCreate,
    ShoppingListEntry,
    ShoppingListEntryCreate,
    ShoppingListWithEntries,
)

router = APIRouter(prefix='/api/collections/{collection_id}/lists', tags=['Shopping Lists'])


@router.post('/', status_code=status.HTTP_201_CREATED, summary='Create a new shopping list')
async def create_shopping_list(
    collection_id: UUID, list_data: ShoppingListCreate, user: GetUser, shopping_list_service: ShoppingListServiceDep
) -> ShoppingListWithEntries:
    return await shopping_list_service.create_list(list_data, collection_id, user)


@router.get('/{list_id}', summary='Get a specific shopping list')
async def get_shopping_list(
    list_id: UUID, user: GetUser, shopping_list_service: ShoppingListServiceDep
) -> ShoppingListWithEntries:
    return await shopping_list_service.get_list(list_id, user)


@router.patch('/{list_id}', summary="Update a shopping list's title")
async def update_shopping_list(
    collection_id: UUID,
    list_id: UUID,
    list_data: ShoppingListCreate,
    user: GetUser,
    shopping_list_service: ShoppingListServiceDep,
) -> ShoppingListWithEntries:
    return await shopping_list_service.update_list(list_data, list_id, collection_id, user)


@router.post('/{list_id}/entries', status_code=status.HTTP_201_CREATED, summary='Add an entry to a shopping list')
async def add_entry_to_shopping_list(
    list_id: UUID, entry_data: ShoppingListEntryCreate, user: GetUser, shopping_list_service: ShoppingListServiceDep
) -> ShoppingListEntry:
    return await shopping_list_service.add_entry_to_list(entry_data, list_id, user)


@router.post(
    '/{list_id}/entries/{entry_id}/complete',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Mark an entry as completed',
)
async def set_entry_completed(
    list_id: UUID, entry_id: UUID, user: GetUser, shopping_list_service: ShoppingListServiceDep
) -> Response:
    await shopping_list_service.set_list_entry_completed(entry_id, list_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    '/{list_id}/entries/{entry_id}/complete',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Mark an entry as not completed',
)
async def unset_entry_completed(
    list_id: UUID, entry_id: UUID, user: GetUser, shopping_list_service: ShoppingListServiceDep
) -> Response:
    await shopping_list_service.unset_list_entry_completed(entry_id, list_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
