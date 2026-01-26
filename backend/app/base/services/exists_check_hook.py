import uuid
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.base.exceptions.basic import NotFoundException
from app.base.repos.base import UpdateSchemaType
from app.base.services.base import BaseUpdateHooks, BaseDeleteHooks, TContextKwargs


class ExistsCheckHooksMixin(BaseUpdateHooks, BaseDeleteHooks):

    @asynccontextmanager
    async def _context_update(self, session: AsyncSession, obj_id: uuid.UUID, obj_data: UpdateSchemaType,
                              context: TContextKwargs):
        if not await self.repo.get_by_pk(session, obj_id):
            raise NotFoundException(
                log_message=f"{self.repo.model_repr(obj_id)} does not exist."
            )
        yield

    @asynccontextmanager
    async def _context_delete(self, session: AsyncSession, obj_id: uuid.UUID, context: TContextKwargs):
        if await self.repo.get_by_pk(session, obj_id) is None:
            raise NotFoundException(
                log_message=f"{self.repo.model_repr(obj_id)} does not exist."
            )

        yield
