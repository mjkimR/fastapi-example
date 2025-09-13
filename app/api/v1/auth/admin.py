import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps.auth import get_current_user, on_superuser
from app.core.deps.params.page import PaginationParam
from app.core.exceptions.exceptions import NotFoundException
from app.models.users import User
from app.schemas.users import UserRead, UsersRead, UserCreate
from app.usecase.users.admin import (
    GetMultiUserUseCase,
    CreateUserUseCase,
    CreateAdminUseCase,
    DeleteUserUseCase,
)

router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(on_superuser)]
)


@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_user(
        user_in: UserCreate,
        use_case: Annotated[CreateUserUseCase, Depends()],
):
    """Create new user."""
    user = await use_case.execute(obj_data=user_in)
    return user


@router.post("/admin", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_admin(
        user_in: UserCreate,
        use_case: Annotated[CreateAdminUseCase, Depends()],
):
    """Create new admin user."""
    user = await use_case.execute(obj_data=user_in)
    return user


@router.get("/", response_model=UsersRead)
async def read_users(
        pagination: PaginationParam,
        use_case: Annotated[GetMultiUserUseCase, Depends()],
):
    """Get user list."""
    users = await use_case.execute(**pagination)
    return users


@router.delete("/{user_id}")
async def delete_user(
        use_case: Annotated[DeleteUserUseCase, Depends()],
        user_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_user)],
):
    if await use_case.execute(user_id, current_user):
        return {"detail": f"User with id {user_id} has been deleted"}
    else:
        raise NotFoundException()
