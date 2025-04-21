# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from psycopg import AsyncCursor, IntegrityError
from psycopg.rows import DictRow

from tests.repository.conftest import AsciiLetterString
from tso_api.repository import user_repository


async def test_create_user(cur: AsyncCursor[DictRow], ascii_letter_string: AsciiLetterString):
    iss = ascii_letter_string(30)
    sub = ascii_letter_string(30)
    await user_repository.create_user(sub, iss, cur)

    res = await (await cur.execute('SELECT * FROM users WHERE issuer = %s and subject = %s', (iss, sub))).fetchone()

    assert res is not None
    assert res['issuer'] == iss
    assert res['subject'] == sub


@pytest.mark.parametrize(('iss', 'sub'), [('test', ''), ('', 'test')], ids=['empty_sub', 'empty_iss'])
async def test_create_user_empty(cur: AsyncCursor[DictRow], iss: str, sub: str):
    with pytest.raises(IntegrityError):
        await user_repository.create_user(sub, iss, cur)


async def test_get_user(cur: AsyncCursor[DictRow], ascii_letter_string: AsciiLetterString):
    iss = ascii_letter_string(30)
    sub = ascii_letter_string(30)
    await user_repository.create_user(sub, iss, cur)

    res = await user_repository.get_user(sub, iss, cur)

    assert res is not None
    assert res['issuer'] == iss
    assert res['subject'] == sub


async def test_get_nonexistant_user(cur: AsyncCursor[DictRow], ascii_letter_string: AsciiLetterString):
    res = await user_repository.get_user(ascii_letter_string(20), ascii_letter_string(20), cur)

    assert res is None
