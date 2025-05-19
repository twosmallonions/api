from typing import Any
from fastapi import APIRouter
from pydantic import PositiveInt

from tso_api.dependency import GetUser, UserServiceDep
from tso_api.models.user import UserResponse

router = APIRouter(prefix='/api/user', tags=['User'])


@router.get('/', response_model=list[UserResponse])
async def get_all_users(
    user: GetUser,
    user_service: UserServiceDep,
    exclude_self: bool = False,
    search: str | None = None,
    limit: PositiveInt = 50,
) -> Any:
    return await user_service.get_all_users(user.id if exclude_self else None, search, limit)
