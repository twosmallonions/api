from collections.abc import Awaitable, Callable
from uuid import UUID

import pytest
from psycopg import AsyncConnection, AsyncCursor
from psycopg.rows import DictRow, dict_row

from tests.repository.conftest import AsciiLetterString, UserColFn
from tso_api.models.user import User
from tso_api.repository import shopping_list_repository

UserListFn = Callable[[AsyncCursor[DictRow], AsciiLetterString], Awaitable[tuple[User, UUID, UUID]]]


@pytest.fixture
def user_list_fn(user_col_fn: UserColFn):
    async def __create(cur: AsyncCursor[DictRow], ascii_letter_string: AsciiLetterString) -> tuple[User, UUID, UUID]:
        user, coll = await user_col_fn(cur)
        new_list = await shopping_list_repository.create_list(ascii_letter_string(30), coll, cur)

        return (user, coll, new_list['id'])

    return __create


async def set_perms(user_id: UUID, cur: AsyncCursor[DictRow]):
    await cur.execute('SET LOCAL ROLE tso_api_user')
    await cur.execute('SELECT tso.set_uid(%s)', (user_id,))


async def create_list(user: User, coll_id: UUID, ascii_letter_string: AsciiLetterString, cur: AsyncCursor[DictRow]):
    await set_perms(user.id, cur)
    return await shopping_list_repository.create_list(ascii_letter_string(30), coll_id, cur)


async def test_create_shopping_list(
    user_col: tuple[User, UUID], ascii_letter_string: AsciiLetterString, conn: AsyncConnection
):
    user, coll = user_col

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await create_list(user, coll, ascii_letter_string, cur)


async def test_update_shopping_list(
    user_col: tuple[User, UUID], ascii_letter_string: AsciiLetterString, conn: AsyncConnection
):
    user, coll = user_col

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        new_list = await create_list(user, coll, ascii_letter_string, cur)
        new_list_id = new_list['id']

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await shopping_list_repository.update_list('UPDATED', new_list_id, coll, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        res = await (await cur.execute('SELECT * FROM tso.shopping_list WHERE id = %s', (new_list_id,))).fetchone()

        assert res
        assert res['id'] == new_list_id
        assert res['title'] == 'UPDATED'


async def test_add_entry(user_list_fn: UserListFn, ascii_letter_string: AsciiLetterString, conn: AsyncConnection):
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        user, coll, s_list = await user_list_fn(cur, ascii_letter_string)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)

        for i in range(30):
            await shopping_list_repository.add_entry_to_list(f'${i} entry', s_list, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        res = await (await cur.execute('SELECT * FROM tso.list_entry WHERE list_id = %s', (s_list,))).fetchall()

        assert len(res) == 30


async def test_get_list(user_list_fn: UserListFn, ascii_letter_string: AsciiLetterString, conn: AsyncConnection):
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        user, coll, s_list = await user_list_fn(cur, ascii_letter_string)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)

        for i in range(30):
            await shopping_list_repository.add_entry_to_list(f'${i} entry', s_list, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        res = await shopping_list_repository.get_list(s_list, cur)

    assert res
    assert res['id'] == s_list
    assert len(res['entries']) == 30
    assert res['num_entries'] == 30


async def test_toggle_completed(
    user_list_fn: UserListFn, ascii_letter_string: AsciiLetterString, conn: AsyncConnection
):
    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        user, coll, s_list = await user_list_fn(cur, ascii_letter_string)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        list_entry = await shopping_list_repository.add_entry_to_list('entry', s_list, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        await shopping_list_repository.set_list_entry_completed(list_entry['id'], s_list, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        res = await shopping_list_repository.get_list(s_list, cur)

        assert res['entries'][0]['completed']
        assert res['entries'][0]['completed_at']

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        await shopping_list_repository.unset_list_entry_completed(list_entry['id'], s_list, cur)

    async with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
        await set_perms(user.id, cur)
        res = await shopping_list_repository.get_list(s_list, cur)

        assert not res['entries'][0]['completed']
        assert not res['entries'][0]['completed_at']
