from uuid import UUID

import pytest
from psycopg import AsyncConnection, AsyncCursor, IntegrityError
from psycopg.errors import CheckViolation, InsufficientPrivilege
from psycopg.rows import DictRow, dict_row

from tests.repository.conftest import AsciiLetterString, UserFn
from tso_api.repository import collection_repository


async def set_perms(user_id: UUID, cur: AsyncCursor[DictRow]):
    await cur.execute('SET LOCAL ROLE tso_api_user')
    await cur.execute('SELECT tso.set_uid(%s)', (user_id, ))


async def test_new_collection_without_owner_throws_error(ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    with pytest.raises(CheckViolation):
        async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
            await collection_repository.new_collection(ascii_letter_string(30), cur)


async def test_new_collection(user: UserFn, ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        u = await user(cur)
        await set_perms(u.id, cur)
        coll_name = ascii_letter_string(20)
        coll_id = await collection_repository.new_collection(coll_name, cur)
        await collection_repository.add_collection_owner(coll_id, u.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(u.id, cur)
        res = await (await raw_conn.cursor(row_factory=dict_row).execute("SELECT * FROM tso.collections WHERE name = %s", (coll_name,))).fetchone()

    assert res
    assert res['name'] == coll_name


async def test_new_repository_empty_name(user: UserFn, raw_conn: AsyncConnection):
        cur = raw_conn.cursor(row_factory=dict_row)
        u = await user(cur)
        await set_perms(u.id, cur)
        with pytest.raises(IntegrityError):
           await collection_repository.new_collection('', cur)


async def test_add_collection_member(user: UserFn, ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        coll_user = await user(cur)
        coll_user2 = await user(cur)
        coll_user3 = await user(cur)

        await set_perms(coll_user.id, cur)

        coll_name = ascii_letter_string(20)
        coll_id = await collection_repository.new_collection(coll_name, cur)
        await collection_repository.add_collection_owner(coll_id, coll_user.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_user.id, cur)
        await collection_repository.add_collection_member(coll_id, coll_user2.id, cur)
        await collection_repository.add_collection_member(coll_id, coll_user3.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_user.id, cur)
        res = await cur.execute("SELECT count(*) AS num_members FROM tso.collection_members WHERE collection = %s", (coll_id,))
        res = await res.fetchone()

        assert res
        assert res['num_members'] == 3

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_user2.id, cur)
        res = await collection_repository.get_collections_for_user(cur)
        assert len(res) == 1


async def test_member_can_only_see_users_from_their_own_collections(user: UserFn, ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        coll_user = await user(cur)
        coll_user2 = await user(cur)

        await set_perms(coll_user.id, cur)

        coll_name = ascii_letter_string(20)
        coll_id = await collection_repository.new_collection(coll_name, cur)
        await collection_repository.add_collection_owner(coll_id, coll_user.id, cur)
        await collection_repository.add_collection_member(coll_id, coll_user2.id, cur)

        coll_name = ascii_letter_string(20)
        coll_id2 = await collection_repository.new_collection(coll_name, cur)
        await collection_repository.add_collection_owner(coll_id2, coll_user.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_user2.id, cur)
        res = await cur.execute("SELECT *  FROM tso.collection_members")
        res = await res.fetchall()

        assert len(res) == 2

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_user.id, cur)
        res = await cur.execute("SELECT *  FROM tso.collection_members")
        res = await res.fetchall()

        assert len(res) == 3


async def test_normal_collection_member_cant_add_member(user: UserFn, ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        coll_owner = await user(cur)
        coll_member = await user(cur)
        coll_member2 = await user(cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_owner.id, cur)
        coll_id = await collection_repository.new_collection(ascii_letter_string(50), cur)
        await collection_repository.add_collection_owner(coll_id, coll_owner.id, cur)
        await collection_repository.add_collection_member(coll_id, coll_member.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_member.id, cur)

        with pytest.raises(InsufficientPrivilege):
            await collection_repository.add_collection_member(coll_id, coll_member2.id, cur)


async def test_update_collection(user: UserFn, ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        u = await user(cur)
        await set_perms(u.id, cur)
        coll_name = ascii_letter_string(20)
        coll_id = await collection_repository.new_collection(coll_name, cur)
        await collection_repository.add_collection_owner(coll_id, u.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        new_name = ascii_letter_string(50)
        await set_perms(u.id, cur)
        await collection_repository.edit_collection(coll_id, new_name, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        coll = await collection_repository.get_collection_by_id(coll_id, cur)

        assert coll
        assert coll['name'] == new_name


async def test_normal_member_cannot_edit(user: UserFn, ascii_letter_string: AsciiLetterString, raw_conn: AsyncConnection):
    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        coll_owner = await user(cur)
        coll_member = await user(cur)
        await set_perms(coll_owner.id, cur)
        coll_name = ascii_letter_string(20)
        coll_id = await collection_repository.new_collection(coll_name, cur)
        await collection_repository.add_collection_owner(coll_id, coll_owner.id, cur)
        await collection_repository.add_collection_member(coll_id, coll_member.id, cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        await set_perms(coll_member.id, cur)
        await collection_repository.edit_collection(coll_id, ascii_letter_string(50), cur)

    async with raw_conn.transaction(), raw_conn.cursor(row_factory=dict_row) as cur:
        coll = await collection_repository.get_collection_by_id(coll_id, cur)

        assert coll
        assert coll['name'] == coll_name
