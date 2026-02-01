from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_kit.base.usecases.crud import (
    BaseCreateUseCase,
    BaseDeleteUseCase,
    BaseGetMultiUseCase,
    BaseGetUseCase,
    BaseUpdateUseCase,
)
from app.features.memos.models import Memo
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.features.memos.services import MemoContextKwargs, MemoService
from app.features.tags.services import TagService


class GetMemoUseCase(BaseGetUseCase[MemoService, Memo, MemoContextKwargs]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)


class GetMultiMemoUseCase(BaseGetMultiUseCase[MemoService, Memo, MemoContextKwargs]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)


class CreateMemoUseCase(BaseCreateUseCase[MemoService, Memo, MemoCreate, MemoContextKwargs]):
    def __init__(
        self,
        service: Annotated[MemoService, Depends()],
        tag_service: Annotated[TagService, Depends()],
    ) -> None:
        super().__init__(service)
        self.tag_service = tag_service

    async def _post_execute(
        self,
        session: AsyncSession,
        obj: Memo,
        obj_data: MemoCreate,
        context: MemoContextKwargs | None,
    ) -> Memo:
        if obj_data.tags:
            tags = await self.tag_service.get_or_create_tags(session, obj_data.tags, context)
            obj.tags = tags
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
        return await super()._post_execute(session, obj, obj_data, context)


class UpdateMemoUseCase(BaseUpdateUseCase[MemoService, Memo, MemoUpdate, MemoContextKwargs]):
    def __init__(
        self,
        service: Annotated[MemoService, Depends()],
        tag_service: Annotated[TagService, Depends()],
    ) -> None:
        super().__init__(service)
        self.tag_service = tag_service

    async def _post_execute(
        self,
        session: AsyncSession,
        obj: Memo | None,
        obj_data: MemoUpdate,
        context: MemoContextKwargs | None,
    ) -> Memo | None:
        if obj and obj_data.tags is not None:
            tags = await self.tag_service.get_or_create_tags(session, obj_data.tags, context)
            obj.tags = tags
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
        return await super()._post_execute(session, obj, obj_data, context)


class DeleteMemoUseCase(BaseDeleteUseCase[MemoService, Memo, MemoContextKwargs]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)
