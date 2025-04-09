from uuid import UUID

import pytest
from psycopg import AsyncCursor, IntegrityError
from psycopg.rows import DictRow

from tests.repository.conftest import AsciiLetterString, UserFn
from tso_api.repository import collection_repository


async def test_new_repository(ascii_letter_string: AsciiLetterString, cur: AsyncCursor[DictRow]):
    coll_name = ascii_letter_string(20)
    await collection_repository.new_collection(coll_name, cur)

    res = await (await cur.execute("SELECT * FROM collections WHERE name = %s", (coll_name,))).fetchone()

    assert res is not None
    assert res['name'] == coll_name


async def test_new_repository_empty_name(cur: AsyncCursor[DictRow]):
    with pytest.raises(IntegrityError):
        await collection_repository.new_collection('', cur)


async def test_add_collection_member(user: UserFn, ascii_letter_string: AsciiLetterString, cur: AsyncCursor[DictRow]):
    coll_user = await user(cur)
    coll_user2 = await user(cur)
    coll_user3 = await user(cur)

    coll_name = ascii_letter_string(20)
    await collection_repository.new_collection(coll_name, cur)
    coll_id = (await collection_repository.get_collection_by_name(coll_name, cur))
    assert coll_id
    coll_id = coll_id['id']

    await collection_repository.add_collection_member(coll_id, coll_user.id, cur)
    await collection_repository.add_collection_member(coll_id, coll_user2.id, cur)
    await collection_repository.add_collection_member(coll_id, coll_user3.id, cur)

    res = await cur.execute("SELECT count(*) AS num_members FROM collection_members WHERE collection = %s", (coll_id,))
    res = await res.fetchone()

    assert res
    assert res['num_members'] == 3


async def test_get_collections_for_user(user: UserFn, ascii_letter_string: AsciiLetterString, cur: AsyncCursor[DictRow]):
    coll_user = await user(cur)

    for _ in range(4):
        coll_name = ascii_letter_string(20)
        await collection_repository.new_collection(coll_name, cur)
        coll_id = (await collection_repository.get_collection_by_name(coll_name, cur))
        assert coll_id
        coll_id = coll_id['id']

    collections: set[UUID] = set()
    for _ in range(4):
        coll_name = ascii_letter_string(20)
        await collection_repository.new_collection(coll_name, cur)
        coll_id = (await collection_repository.get_collection_by_name(coll_name, cur))
        assert coll_id
        coll_id = coll_id['id']

        await collection_repository.add_collection_member(coll_id, coll_user.id, cur)

        collections.add(coll_id)

    res = await collection_repository.get_collections_for_user(coll_user.id, cur)

    assert {row['id'] for row in res} == collections
