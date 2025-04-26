# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from psycopg.rows import DictRow

from tso_api.models.user import User
from tso_api.repository import collection_repository, user_repository
from tso_api.service.base_service import BaseService


class UserService(BaseService):
    async def get_or_create_user(self, subject: str, issuer: str):
        async with self._begin_unsafe() as cur:
            res = await user_repository.get_user(subject, issuer, cur)
            if res is None:
                res = await user_repository.create_user(subject, issuer, cur)

                coll_id = (await collection_repository.new_collection('Default', cur))['id']
                await collection_repository.add_collection_owner(coll_id, res['id'], cur)

        return _user_from_row(res)


def _user_from_row(row: DictRow) -> User:
    return User(id=row['id'], subject=row['subject'], issuer=row['issuer'], created_at=row['created_at'])
