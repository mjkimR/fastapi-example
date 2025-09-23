from uuid import UUID
from typing import Any, Union, TypeVar, Generic, Optional

from app.repos.base import ModelType, CreateSchemaType, UpdateSchemaType
from app.schemas.base import PaginatedList
from app.services.base.basic import (
    BasicCreateServiceMixin, BasicGetServiceMixin, BasicGetMultiServiceMixin, BasicUpdateServiceMixin,
    BasicDeleteServiceMixin
)
from app.core.transaction import AsyncTransaction
from app.usecase.base.base import BaseUseCase

TService = TypeVar("TService", bound=Union[
    BasicCreateServiceMixin,
    BasicGetServiceMixin,
    BasicGetMultiServiceMixin,
    BasicUpdateServiceMixin,
    BasicDeleteServiceMixin,
    Any
])


class BaseGetUseCase(BaseUseCase, Generic[TService, ModelType]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_id: UUID) -> Optional[ModelType]:
        async with AsyncTransaction() as session:
            return await self.service.get(session, obj_id)


class BaseGetMultiUseCase(BaseUseCase, Generic[TService, ModelType]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, offset, limit, order_by=None, where=None) -> PaginatedList[ModelType]:
        async with AsyncTransaction() as session:
            return await self.service.get_multi(session, offset=offset, limit=limit, order_by=order_by, where=where)


class BaseCreateUseCase(BaseUseCase, Generic[TService, ModelType, CreateSchemaType]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_data: CreateSchemaType) -> ModelType:
        async with AsyncTransaction() as session:
            return await self.service.create(session, obj_data)


class BaseUpdateUseCase(BaseUseCase, Generic[TService, ModelType, UpdateSchemaType]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_id: UUID, obj_data: UpdateSchemaType) -> ModelType:
        async with AsyncTransaction() as session:
            return await self.service.update(session, obj_id, obj_data)


class BaseDeleteUseCase(BaseUseCase, Generic[TService, ModelType]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_id: UUID):
        async with AsyncTransaction() as session:
            return await self.service.delete(session, obj_id)
