from typing import Any

from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from tso_api.models.user import User
from tso_api.repository import collection_repository, user_repository
from tso_api.service.base_service import BaseService, NoneAfterInsertError, ResourceNotFoundError


class UserService(BaseService):
    def __init__(self, pool: AsyncConnectionPool[Any]) -> None:
        super().__init__(pool)

    async def get_or_create_user(self, subject: str, issuer: str):
        async with self.begin() as cur:
            res = await user_repository.get_user(subject, issuer, cur)
            if res is None:
                res = await user_repository.create_user(subject, issuer, cur)
                if res is None:
                    msg = 'user'
                    raise NoneAfterInsertError(msg) from None

                coll_id = await collection_repository.new_collection('Default', cur)
                await collection_repository.add_collection_member(coll_id, res['id'], cur)

        return _user_from_row(res)


def _user_from_row(row: DictRow) -> User:
    return User(id=row['id'], subject=row['subject'], issuer=row['issuer'], created_at=row['created_at'])
