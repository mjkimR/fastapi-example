from typing import Generic, TypeVar
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repos.base import BaseRepository, ModelType, CreateSchemaType, UpdateSchemaType, GetMultiResponseModel

TRepo = TypeVar("TRepo", bound=BaseRepository)


class BaseService(Generic[TRepo, ModelType, CreateSchemaType, UpdateSchemaType]):
    repo: TRepo

    def __init__(self, repo: TRepo):
        self.repo = repo

    async def get_by_id(self, session: AsyncSession, obj_id: uuid.UUID) -> ModelType:
        """Retrieve a single object by its primary key and return as ModelType."""
        return await self.repo.get_by_pk(session, pk=obj_id)

    async def get_multi(self, session: AsyncSession, offset: int = 0, limit: int = 100) -> GetMultiResponseModel:
        """Retrieve multiple objects with pagination and return as GetMultiResponseModel."""
        return await self.repo.get_multi(session, offset=offset, limit=limit)

    async def create(self, session: AsyncSession, obj_data: CreateSchemaType) -> ModelType:
        """Create a new object and return as ModelType."""
        return await self.repo.create(session, obj_in=obj_data, commit=True)

    async def update_by_id(self, session: AsyncSession, obj_id: uuid.UUID, obj_data: UpdateSchemaType) -> ModelType:
        """Update an existing object by its primary key and return as ModelType."""
        return await self.repo.update_by_pk(session, pk=obj_id, obj_in=obj_data, commit=True)

    async def delete_by_id(self, session: AsyncSession, obj_id: uuid.UUID) -> bool:
        """Delete an object by its primary key and return a boolean indicating success."""
        return await self.repo.delete_by_pk(session, pk=obj_id, commit=True, soft_delete=False)
