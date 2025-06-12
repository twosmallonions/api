from collections.abc import Callable
from typing import Any
from uuid import UUID

import httpx
import pytest

from tests.api.conftest import UUID4Factory
from tso_api.models.shopping_list import ShoppingListCreate, ShoppingListEntryCreate

ShoppingListFactory = Callable[[], dict[str, Any]]


@pytest.fixture
def shopping_list_factory(client: httpx.Client, uuid4_factory: UUID4Factory, collection: dict[str, Any]):
    def _do():
        title = uuid4_factory()
        shopping_list_create = ShoppingListCreate(title=title)

        resp = client.post(f'/api/collections/{collection["id"]}/lists/', json=shopping_list_create.model_dump())
        resp.raise_for_status()

        assert resp.status_code == 201

        return resp.json()

    return _do


@pytest.fixture
def shopping_list(shopping_list_factory: ShoppingListFactory):
    return shopping_list_factory()


# Type aliases
ShoppingListEntryFactory = Callable[[], dict[str, Any]]


@pytest.fixture
def shopping_list_entry_factory(
    client: httpx.Client, shopping_list: dict[str, Any], uuid4_factory: UUID4Factory
) -> ShoppingListEntryFactory:
    """Factory to create shopping list entries"""

    def create_entry(name: str | None = None) -> dict[str, Any]:
        if name is None:
            name = str(uuid4_factory())

        entry_create = ShoppingListEntryCreate(name=name)
        collection_id = shopping_list['collectionId']
        list_id = shopping_list['id']

        resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries', json=entry_create.model_dump())
        resp.raise_for_status()
        return resp.json()

    return create_entry


@pytest.fixture
def shopping_list_entry(shopping_list_entry_factory: ShoppingListEntryFactory) -> dict[str, Any]:
    """Create a single shopping list entry for testing"""
    return shopping_list_entry_factory()


def test_create_shopping_list(client: httpx.Client, uuid4_factory: UUID4Factory, collection: dict[str, Any]):
    title = uuid4_factory()
    shopping_list_create = ShoppingListCreate(title=title)

    resp = client.post(f'/api/collections/{collection["id"]}/lists', json=shopping_list_create.model_dump())
    resp.raise_for_status()

    assert resp.status_code == 201


def test_get_shopping_list(client: httpx.Client, shopping_list: dict[str, Any]):
    collection = shopping_list['collectionId']

    list_id: str = shopping_list['id']
    resp = client.get(f'/api/collections/{collection}/lists/{list_id}')

    resp.raise_for_status()

    resp_json = resp.json()
    id_uuid = UUID(resp_json['id'])
    assert id_uuid.version == 7
    assert resp_json['title'] == shopping_list['title']


def test_get_shopping_lists(
    client: httpx.Client, shopping_list_factory: ShoppingListFactory, shopping_list: dict[str, Any]
):
    create_n = 10
    collection = shopping_list['collectionId']
    ids = [shopping_list_factory()['id'] for _ in range(create_n)]
    for _ in range(create_n):
        shopping_list_factory()

    resp = client.get(f'/api/collections/{collection}/lists')

    resp.raise_for_status()

    resp_json = resp.json()

    assert set(ids) <= {r['id'] for r in resp_json}


def test_create_shopping_list_entry(client: httpx.Client, shopping_list: dict[str, Any], uuid4_factory: UUID4Factory):
    name = str(uuid4_factory())
    entry_create = ShoppingListEntryCreate(name=name)

    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']

    resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries', json=entry_create.model_dump())
    resp.raise_for_status()

    assert resp.status_code == 201

    resp_json: dict[str, Any] = resp.json()
    id_uuid = UUID(resp_json['id'])
    assert id_uuid.version == 7
    assert resp_json['name'] == name
    assert resp_json['completed'] is False
    assert resp_json['completedAt'] is None


def test_create_multiple_shopping_list_entries(
    client: httpx.Client, shopping_list: dict[str, Any], uuid4_factory: UUID4Factory
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']

    entries_to_create = 5
    created_names: list[str] = []

    for _ in range(entries_to_create):
        name = str(uuid4_factory())
        created_names.append(name)
        entry_create = ShoppingListEntryCreate(name=name)

        resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries', json=entry_create.model_dump())
        resp.raise_for_status()
        assert resp.status_code == 201

    # Verify all entries exist by getting the shopping list
    resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
    resp.raise_for_status()

    resp_json: dict[str, Any] = resp.json()
    entry_names: set[str] = {entry['name'] for entry in resp_json['entries']}

    assert set(created_names) <= entry_names


def test_complete_shopping_list_entry(
    client: httpx.Client, shopping_list: dict[str, Any], shopping_list_entry: dict[str, Any]
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']
    entry_id: str = shopping_list_entry['id']

    resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_id}/complete')
    resp.raise_for_status()

    assert resp.status_code == 204

    # Verify entry is marked as completed
    resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
    resp.raise_for_status()

    resp_json: dict[str, Any] = resp.json()
    entry: dict[str, Any] | None = next((e for e in resp_json['entries'] if e['id'] == entry_id), None)
    assert entry is not None
    assert entry['completed'] is True
    assert entry['completedAt'] is not None


def test_uncomplete_shopping_list_entry(
    client: httpx.Client, shopping_list: dict[str, Any], shopping_list_entry: dict[str, Any]
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']
    entry_id: str = shopping_list_entry['id']

    # First complete the entry
    resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_id}/complete')
    resp.raise_for_status()

    # Then uncomplete it
    resp = client.delete(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_id}/complete')
    resp.raise_for_status()

    assert resp.status_code == 204

    # Verify entry is marked as not completed
    resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
    resp.raise_for_status()

    resp_json: dict[str, Any] = resp.json()
    entry: dict[str, Any] | None = next((e for e in resp_json['entries'] if e['id'] == entry_id), None)
    assert entry is not None
    assert entry['completed'] is False
    assert entry['completedAt'] is None


def test_complete_multiple_entries(
    client: httpx.Client, shopping_list: dict[str, Any], shopping_list_entry_factory: ShoppingListEntryFactory
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']

    # Create multiple entries
    entries: list[dict[str, Any]] = [shopping_list_entry_factory() for _ in range(3)]
    entry_ids: list[str] = [entry['id'] for entry in entries]

    # Complete all entries
    for entry_id in entry_ids:
        resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_id}/complete')
        resp.raise_for_status()
        assert resp.status_code == 204

    # Verify all entries are completed
    resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
    resp.raise_for_status()

    resp_json: dict[str, Any] = resp.json()
    completed_entries: list[dict[str, Any]] = [
        e for e in resp_json['entries'] if e['id'] in entry_ids and e['completed']
    ]
    assert len(completed_entries) == 3


def test_complete_and_uncomplete_workflow(
    client: httpx.Client, shopping_list: dict[str, Any], shopping_list_entry_factory: ShoppingListEntryFactory
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']

    # Create multiple entries
    entries: list[dict[str, Any]] = [shopping_list_entry_factory() for _ in range(4)]
    entry_ids: list[str] = [entry['id'] for entry in entries]

    # Complete first two entries
    for entry_id in entry_ids[:2]:
        resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_id}/complete')
        resp.raise_for_status()

    # Uncomplete first entry
    resp = client.delete(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_ids[0]}/complete')
    resp.raise_for_status()

    # Verify final state
    resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
    resp.raise_for_status()

    resp_json: dict[str, Any] = resp.json()
    entries_dict: dict[str, dict[str, Any]] = {e['id']: e for e in resp_json['entries'] if e['id'] in entry_ids}

    # First entry should be uncompleted
    assert entries_dict[entry_ids[0]]['completed'] is False
    # Second entry should still be completed
    assert entries_dict[entry_ids[1]]['completed'] is True
    # Third and fourth entries should be uncompleted
    assert entries_dict[entry_ids[2]]['completed'] is False
    assert entries_dict[entry_ids[3]]['completed'] is False


def test_shopping_list_with_entries_structure(
    client: httpx.Client, shopping_list: dict[str, Any], shopping_list_entry_factory: ShoppingListEntryFactory
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']

    # Create entries with different completion states
    entry1: dict[str, Any] = shopping_list_entry_factory()
    entry2: dict[str, Any] = shopping_list_entry_factory()

    # Complete first entry
    resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry1["id"]}/complete')
    resp.raise_for_status()

    # Get shopping list and verify structure
    resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
    resp.raise_for_status()

    resp_json: dict[str, Any] = resp.json()

    # Verify shopping list structure
    assert 'entries' in resp_json
    assert 'entriesNum' in resp_json
    assert len(resp_json['entries']) == 2
    assert resp_json['entriesNum'] == 2

    # Verify entry structure
    entry1_found = False
    entry2_found = False

    for entry in resp_json['entries']:
        if entry['id'] == entry1['id']:
            assert entry['completed'] is True
            assert entry['completedAt'] is not None
            entry1_found = True
        elif entry['id'] == entry2['id']:
            assert entry['completed'] is False
            assert entry['completedAt'] is None
            entry2_found = True

    assert entry1_found
    assert entry2_found


def test_entry_completion_state_persistence(
    client: httpx.Client, shopping_list: dict[str, Any], shopping_list_entry_factory: ShoppingListEntryFactory
):
    collection_id: str = shopping_list['collectionId']
    list_id: str = shopping_list['id']

    # Create an entry and complete it
    entry: dict[str, Any] = shopping_list_entry_factory()
    entry_id: str = entry['id']

    # Complete entry
    resp = client.post(f'/api/collections/{collection_id}/lists/{list_id}/entries/{entry_id}/complete')
    resp.raise_for_status()

    # Fetch list multiple times to ensure completion state persists
    for _ in range(3):
        resp = client.get(f'/api/collections/{collection_id}/lists/{list_id}')
        resp.raise_for_status()

        resp_json: dict[str, Any] = resp.json()
        found_entry: dict[str, Any] | None = next((e for e in resp_json['entries'] if e['id'] == entry_id), None)
        assert found_entry is not None
        assert found_entry['completed'] is True
        assert found_entry['completedAt'] is not None
