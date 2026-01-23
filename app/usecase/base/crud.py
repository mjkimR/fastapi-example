from uuid import UUID
from typing import Any, Union, TypeVar, Generic, Optional

from app.repos.base import ModelType, CreateSchemaType, UpdateSchemaType
from app.schemas.base import PaginatedList
from app.services.base.base import (
    BaseCreateServiceMixin, BaseGetServiceMixin, BaseGetMultiServiceMixin, BaseUpdateServiceMixin,
    BaseDeleteServiceMixin, TContextKwargs
)
from app.core.transaction import AsyncTransaction
from app.usecase.base.base import BaseUseCase

TService = TypeVar("TService", bound=Union[
    BaseCreateServiceMixin,
    BaseGetServiceMixin,
    BaseGetMultiServiceMixin,
    BaseUpdateServiceMixin,
    BaseDeleteServiceMixin,
    Any
])


class BaseGetUseCase(BaseUseCase, Generic[TService, ModelType, TContextKwargs]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_id: UUID, context: Optional[TContextKwargs] = None) -> Optional[ModelType]:
        async with AsyncTransaction() as session:
            return await self.service.get(session, obj_id, context=context)


class BaseGetMultiUseCase(BaseUseCase, Generic[TService, ModelType, TContextKwargs]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(
            self, offset: int, limit: int, order_by=None, where=None, context: Optional[TContextKwargs] = None
    ) -> PaginatedList[ModelType]:
        async with AsyncTransaction() as session:
            return await self.service.get_multi(
                session, offset=offset, limit=limit, order_by=order_by, where=where, context=context
            )


class BaseCreateUseCase(BaseUseCase, Generic[TService, ModelType, CreateSchemaType, TContextKwargs]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_data: CreateSchemaType, context: Optional[TContextKwargs] = None) -> ModelType:
        async with AsyncTransaction() as session:
            return await self.service.create(session, obj_data, context=context)


class BaseUpdateUseCase(BaseUseCase, Generic[TService, ModelType, UpdateSchemaType, TContextKwargs]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(
            self, obj_id: UUID, obj_data: UpdateSchemaType, context: Optional[TContextKwargs] = None
    ) -> ModelType:
        async with AsyncTransaction() as session:
            return await self.service.update(session, obj_id, obj_data, context=context)


class BaseDeleteUseCase(BaseUseCase, Generic[TService, ModelType, TContextKwargs]):
    def __init__(self, service: TService):
        self.service = service

    async def execute(self, obj_id: UUID, context: Optional[TContextKwargs] = None):
        async with AsyncTransaction() as session:
            return await self.service.delete(session, obj_id, context=context)
