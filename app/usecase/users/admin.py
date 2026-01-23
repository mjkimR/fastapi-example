from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends
from app.core.transaction import AsyncTransaction

from app.core.exceptions.exceptions import UserCantDeleteItselfException
from app.models.users import User
from app.schemas.users import UserCreate
from app.services.base.base import BaseContextKwargs, TContextKwargs
from app.services.users import UserService
from app.usecase.base.base import BaseUseCase
from app.usecase.base.crud import BaseGetMultiUseCase


class GetMultiUserUseCase(BaseGetMultiUseCase[UserService, User, BaseContextKwargs]):
    def __init__(self, service: Annotated[UserService, Depends()]):
        super().__init__(service)


class DeleteUserUseCase(BaseUseCase):
    def __init__(self, service: Annotated[UserService, Depends()]):
        self.service = service

    async def execute(
            self, user_id: UUID, current_user: User, context: Optional[TContextKwargs] = None
    ) -> bool:
        if current_user.id == user_id:
            raise UserCantDeleteItselfException()
        async with AsyncTransaction() as session:
            return await self.service.delete(session, user_id, context=context)


class CreateUserUseCase(BaseUseCase):
    def __init__(self, service: Annotated[UserService, Depends()]):
        self.service = service

    async def execute(
            self, obj_data: UserCreate, context: Optional[TContextKwargs] = None
    ) -> User:
        async with AsyncTransaction() as session:
            return await self.service.create_user(session, obj_data)


class CreateAdminUseCase(BaseUseCase):
    def __init__(self, service: Annotated[UserService, Depends()]):
        self.service = service

    async def execute(
            self, obj_data: UserCreate, context: Optional[TContextKwargs] = None
    ) -> User:
        async with AsyncTransaction() as session:
            return await self.service.create_admin(session, obj_data)