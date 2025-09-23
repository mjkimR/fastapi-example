from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.transaction import AsyncTransaction
from app.models.memos import Memo
from app.schemas.memos import MemoCreate, MemoUpdate
from app.services.memos import MemoService
from app.services.tags import TagService
from app.usecase.base.crud import (
    BaseGetUseCase,
    BaseGetMultiUseCase,
    BaseDeleteUseCase,
)


class GetMemoUseCase(BaseGetUseCase[MemoService, Memo]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)


class GetMultiMemoUseCase(BaseGetMultiUseCase[MemoService, Memo]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)


class CreateMemoUseCase:
    def __init__(
            self,
            memo_service: Annotated[MemoService, Depends()],
            tag_service: Annotated[TagService, Depends()],
    ) -> None:
        self.memo_service = memo_service
        self.tag_service = tag_service

    async def execute(self, obj_in: MemoCreate) -> Memo:
        async with AsyncTransaction() as session:
            tags = await self.tag_service.get_or_create_tags(session, obj_in.tags)

            memo_data_for_create = MemoCreate.model_validate(obj_in.model_dump(exclude={"tags"}))
            memo = await self.memo_service.create(
                session, obj_data=memo_data_for_create
            )
            memo.tags = tags
            await session.commit()
            await session.refresh(memo)
            return memo


class UpdateMemoUseCase:
    def __init__(
            self,
            memo_service: Annotated[MemoService, Depends()],
            tag_service: Annotated[TagService, Depends()],
    ) -> None:
        self.memo_service = memo_service
        self.tag_service = tag_service

    async def execute(self, obj_id: UUID, obj_in: MemoUpdate) -> Memo | None:
        async with AsyncTransaction() as session:
            memo = await self.memo_service.get(session, obj_id)
            if not memo:
                return None

            if obj_in.tags is not None:
                tags = await self.tag_service.get_or_create_tags(
                    session, obj_in.tags
                )
                memo.tags = tags

            update_data = obj_in.model_dump(exclude_unset=True, exclude={"tags"})
            if update_data:
                for field, value in update_data.items():
                    setattr(memo, field, value)

            session.add(memo)
            await session.commit()
            await session.refresh(memo)
            return memo


class DeleteMemoUseCase(BaseDeleteUseCase[MemoService, Memo]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)
