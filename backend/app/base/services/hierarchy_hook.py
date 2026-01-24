from contextlib import asynccontextmanager
from typing import Required

from sqlalchemy.ext.asyncio import AsyncSession

from app.base.exceptions.basic import NotFoundException
from app.base.repos.base import BaseRepository, CreateSchemaType
from app.base.services.base import BaseCreateHooks, BaseContextKwargs, TContextKwargs, BaseUpdateHooks, BaseGetHooks, \
    BaseGetMultiHooks, BaseDeleteHooks


class HierarchicalContextKwargs(BaseContextKwargs):
    """Hierarchical context kwargs."""
    parent_id: Required[str]


class HierarchicalHooks(
    BaseCreateHooks,
    BaseUpdateHooks,
    BaseGetHooks,
    BaseGetMultiHooks,
    BaseDeleteHooks,
):
    repo: BaseRepository
    parent_repo: BaseRepository

    @asynccontextmanager
    async def _context_create(self, session: AsyncSession, obj_data: CreateSchemaType, context: TContextKwargs):
        async with super()._context_create(session, obj_data, context):
            parent_id = context["parent_id"]
            if not await self.parent_repo.get_by_pk(session, parent_id):
                raise NotFoundException(
                    f"Parent {self.parent_repo.model_name}(id={parent_id}) not found for {self.repo.model_name}"
                )
            yield
