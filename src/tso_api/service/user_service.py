# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

from uuid import UUID
from psycopg.rows import DictRow

from tso_api.auth import JWT
from tso_api.models.user import User
from tso_api.repository import collection_repository, user_repository
from tso_api.service.base_service import BaseService


class UserService(BaseService):
    async def get_or_create_user(self, jwt: JWT):
        display_name = jwt.preferred_username or jwt.email or jwt.name or jwt.given_name
        async with self._begin_unsafe() as cur:
            res = await user_repository.get_user(jwt.subject, jwt.issuer, cur)
            if res is None:
                res = await user_repository.create_user(jwt.subject, jwt.issuer, display_name, cur)

                coll_id = (await collection_repository.new_collection('Default', cur))['id']
                await collection_repository.add_collection_owner(coll_id, res['id'], cur)
            elif res['display_name'] != display_name:
                await user_repository.update_user(res['id'], display_name, cur)
                res['display_name'] = display_name

        return _user_from_row(res)

    async def get_all_users(self, user_id: UUID | None, search: str | None, limit: int):
        """
        Return all users.

        :param UUID or None user_id: if not none will return all users except the one specified by user_id
        :return: all users
        """
        async with self._begin_unsafe() as cur:
            res = await user_repository.get_users(cur, user_id, search, limit)

        return [_user_from_row(user) for user in res]


def _user_from_row(row: DictRow) -> User:
    return User(
        id=row['id'],
        subject=row['subject'],
        issuer=row['issuer'],
        created_at=row['created_at'],
        display_name=row['display_name'],
    )
