from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from app.core.exceptions.exceptions import PermissionDeniedException
from app.models.users import User
from app.schemas.users import UserUpdate
from app.services.users import UserService
from app.usecase.base.base import BaseUseCase
from app.core.transaction import AsyncTransaction


class GetUserUseCase(BaseUseCase):
    def __init__(self, service: Annotated[UserService, Depends()]):
        self.service = service

    async def execute(self, user_id: UUID, current_user: User) -> User:
        if current_user.id == user_id:
            return current_user
        if current_user.role != User.Role.ADMIN:
            raise PermissionDeniedException()
        async with AsyncTransaction() as session:
            return await self.service.get(session, user_id)


class UpdateUserUseCase(BaseUseCase):
    def __init__(self, service: Annotated[UserService, Depends()]):
        self.service = service

    async def execute(
            self, obj_data: UserUpdate, user_id: UUID, current_user: User
    ) -> User:
        if current_user.id == user_id:
            return current_user
        if current_user.role != User.Role.ADMIN:
            raise PermissionDeniedException()
        async with AsyncTransaction() as session:
            return await self.service.update_user(session, obj_data, user_id)
