from uuid import UUID
from typing import Any, Union, TypeVar, Generic, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.repos.base import ModelType, CreateSchemaType, UpdateSchemaType
from app.base.schemas.delete_resp import DeleteResponse
from app.base.schemas.paginated import PaginatedList
from app.base.services.base import (
    BaseCreateServiceMixin,
    BaseGetServiceMixin,
    BaseGetMultiServiceMixin,
    BaseUpdateServiceMixin,
    BaseDeleteServiceMixin,
    TContextKwargs,
)
from app.core.database.transaction import AsyncTransaction
from app.base.usecases.base import BaseUseCase

TBaseCreateService = TypeVar(
    "TBaseCreateService", bound=Union[BaseCreateServiceMixin, Any]
)
TBaseGetMultiService = TypeVar(
    "TBaseGetMultiService", bound=Union[BaseGetMultiServiceMixin, Any]
)
TBaseGetService = TypeVar("TBaseGetService", bound=Union[BaseGetServiceMixin, Any])
TBaseUpdateService = TypeVar(
    "TBaseUpdateService", bound=Union[BaseUpdateServiceMixin, Any]
)
TBaseDeleteService = TypeVar(
    "TBaseDeleteService", bound=Union[BaseDeleteServiceMixin, Any]
)


class BaseGetUseCase(BaseUseCase, Generic[TBaseGetService, ModelType, TContextKwargs]):
    def __init__(self, service: TBaseGetService):
        self.service = service

    async def execute(
        self, obj_id: UUID, context: Optional[TContextKwargs] = None
    ) -> Optional[ModelType]:
        async with AsyncTransaction() as session:
            return await self.service.get(session, obj_id, context=context)


class BaseGetMultiUseCase(
    BaseUseCase, Generic[TBaseGetMultiService, ModelType, TContextKwargs]
):
    def __init__(self, service: TBaseGetMultiService):
        self.service = service

    async def execute(
        self,
        offset: int,
        limit: int,
        order_by=None,
        where=None,
        context: Optional[TContextKwargs] = None,
    ) -> PaginatedList[ModelType]:
        async with AsyncTransaction() as session:
            return await self.service.get_multi(
                session,
                offset=offset,
                limit=limit,
                order_by=order_by,
                where=where,
                context=context,
            )


class BaseCreateUseCase(
    BaseUseCase,
    Generic[TBaseCreateService, ModelType, CreateSchemaType, TContextKwargs],
):
    def __init__(self, service: TBaseCreateService):
        self.service = service

    @asynccontextmanager
    async def _context_execute(
        self,
        session: AsyncSession,
        obj_data: CreateSchemaType,
        context: Optional[TContextKwargs],
    ):
        yield

    async def _post_execute(
        self,
        session: AsyncSession,
        obj: ModelType,
        obj_data: CreateSchemaType,
        context: Optional[TContextKwargs],
    ) -> ModelType:
        return obj

    async def execute(
        self, obj_data: CreateSchemaType, context: Optional[TContextKwargs] = None
    ) -> ModelType:
        async with AsyncTransaction() as session:
            async with self._context_execute(session, obj_data, context):
                obj = await self.service.create(session, obj_data, context=context)
                obj = await self._post_execute(session, obj, obj_data, context)
                return obj


class BaseUpdateUseCase(
    BaseUseCase,
    Generic[TBaseUpdateService, ModelType, UpdateSchemaType, TContextKwargs],
):
    def __init__(self, service: TBaseUpdateService):
        self.service = service

    @asynccontextmanager
    async def _context_execute(
        self,
        session: AsyncSession,
        obj_data: UpdateSchemaType,
        context: Optional[TContextKwargs],
    ):
        yield

    async def _post_execute(
        self,
        session: AsyncSession,
        obj: ModelType | None,
        obj_data: UpdateSchemaType,
        context: Optional[TContextKwargs],
    ) -> ModelType | None:
        return obj

    async def execute(
        self,
        obj_id: UUID,
        obj_data: UpdateSchemaType,
        context: Optional[TContextKwargs] = None,
    ) -> ModelType | None:
        async with AsyncTransaction() as session:
            async with self._context_execute(session, obj_data, context):
                obj = await self.service.update(
                    session, obj_id, obj_data, context=context
                )
                obj = await self._post_execute(session, obj, obj_data, context)
                return obj


class BaseDeleteUseCase(
    BaseUseCase, Generic[TBaseDeleteService, ModelType, TContextKwargs]
):
    def __init__(self, service: TBaseDeleteService):
        self.service = service

    @asynccontextmanager
    async def _context_execute(
        self,
        session: AsyncSession,
        obj_id: UUID,
        context: Optional[TContextKwargs],
    ):
        yield

    async def _post_execute(
        self,
        session: AsyncSession,
        obj: DeleteResponse,
        context: Optional[TContextKwargs],
    ) -> DeleteResponse:
        return obj

    async def execute(self, obj_id: UUID, context: Optional[TContextKwargs] = None):
        async with AsyncTransaction() as session:
            async with self._context_execute(session, obj_id, context):
                obj = await self.service.delete(session, obj_id, context=context)
                return await self._post_execute(session, obj, context)
