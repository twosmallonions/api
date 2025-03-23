import pytest
from psycopg import AsyncConnection

from tests.repository.conftest import UserFn
from tso_api.repository import collection_repository


@pytest.mark.collections
async def test_get_collections_for_user_owner(user: UserFn, conn: AsyncConnection):
    user_1 = await user(conn)
    res = await collection_repository.new_collection('test-collection', user_1, conn)
    assert res.name == 'test-collection'

    get_col = await collection_repository.get_collections_for_user(user_1, conn)

    assert len(get_col) == 1
    assert get_col[0].name == 'test-collection'


@pytest.mark.collections
async def test_get_collections_for_user(user: UserFn, conn: AsyncConnection):
    user_1 = await user(conn)
    user_2 = await user(conn)
    res = await collection_repository.new_collection('test-collection', user_1, conn)
    assert res.name == 'test-collection'
    await collection_repository.add_collection_member(res.id, user_2, conn)

    get_col = await collection_repository.get_collections_for_user(user_2, conn)

    assert len(get_col) == 1
    assert get_col[0].name == 'test-collection'
