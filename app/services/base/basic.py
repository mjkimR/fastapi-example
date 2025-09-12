from typing import Generic, TypeVar
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repos.base import BaseRepository, ModelType, CreateSchemaType, UpdateSchemaType
from app.schemas.base import PaginatedList

TRepo = TypeVar("TRepo", bound=BaseRepository)


class BasicCreateServiceMixin(Generic[TRepo, ModelType, CreateSchemaType]):
    repo: TRepo

    async def create(
            self, session: AsyncSession, obj_data: CreateSchemaType
    ) -> ModelType:
        """Create a new object and return as ModelType."""
        return await self.repo.create(session, obj_in=obj_data)


class BasicUpdateServiceMixin(Generic[TRepo, ModelType, UpdateSchemaType]):
    repo: TRepo

    async def update(
            self, session: AsyncSession, obj_id: uuid.UUID, obj_data: UpdateSchemaType
    ) -> ModelType:
        """Update an existing object and return as ModelType."""
        return await self.repo.update_by_pk(session, pk=obj_id, obj_in=obj_data)


class BasicDeleteServiceMixin(Generic[TRepo, ModelType]):
    repo: TRepo

    async def delete(self, session: AsyncSession, obj_id: uuid.UUID) -> bool:
        """Delete an object and return a boolean indicating success."""
        return await self.repo.delete_by_pk(session, pk=obj_id)


class BasicGetServiceMixin(Generic[TRepo, ModelType]):
    repo: TRepo

    async def get(self, session: AsyncSession, obj_id: uuid.UUID) -> ModelType:
        """Retrieve a single object by its primary key and return as ModelType."""
        return await self.repo.get_by_pk(session, pk=obj_id)


class BasicGetMultiServiceMixin(Generic[TRepo, ModelType]):
    repo: TRepo

    async def get_multi(
            self, session: AsyncSession,
            offset: int = 0, limit: int = 100,
            order_by=None, where=None,
    ) -> PaginatedList[ModelType]:
        """Retrieve multiple objects with pagination and return as PaginatedList."""
        return await self.repo.get_multi(
            session, offset=offset, limit=limit, where=where, order_by=order_by
        )
