from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.database.transaction import AsyncTransaction
from app.features.memos.enum import MEMO_RES_NAME, MemoEventType
from app.features.memos.models import Memo
from app.features.memos.schemas import MemoCreate, MemoNotificationPayload, MemoUpdate
from app.features.memos.services import MemoService, MemoContextKwargs
from app.features.tags.services import TagService
from app.features.outbox.services import OutboxService
from app.features.outbox.schemas import OutboxCreate
from app.base.usecases.crud import (
    BaseGetUseCase,
    BaseGetMultiUseCase,
    BaseDeleteUseCase,
)


class GetMemoUseCase(BaseGetUseCase[MemoService, Memo, MemoContextKwargs]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)


class GetMultiMemoUseCase(BaseGetMultiUseCase[MemoService, Memo, MemoContextKwargs]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)


class CreateMemoUseCase:
    def __init__(
        self,
        memo_service: Annotated[MemoService, Depends()],
        tag_service: Annotated[TagService, Depends()],
        outbox_service: Annotated[OutboxService, Depends()],
    ) -> None:
        self.memo_service = memo_service
        self.tag_service = tag_service
        self.outbox_service = outbox_service

    async def execute(self, obj_in: MemoCreate, context: MemoContextKwargs) -> Memo:
        async with AsyncTransaction() as session:
            tags = await self.tag_service.get_or_create_tags(
                session, obj_in.tags, context
            )

            memo_data_for_create = MemoCreate.model_validate(
                obj_in.model_dump(exclude={"tags"})
            )
            memo = await self.memo_service.create(
                session, obj_data=memo_data_for_create, context=context
            )
            memo.tags = tags
            await session.flush()

            # Create and add the outbox event in the same transaction
            event_data = OutboxCreate(
                aggregate_type=MEMO_RES_NAME,
                aggregate_id=str(memo.id),
                event_type=MemoEventType.CREATE,
                payload=MemoNotificationPayload.from_orm(
                    memo, context["user_id"], MemoEventType.CREATE
                ),
            )
            await self.outbox_service.add_event(session, event_data)

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

    async def execute(
        self,
        obj_id: UUID,
        obj_in: MemoUpdate,
        context: MemoContextKwargs,
    ) -> Memo | None:
        async with AsyncTransaction() as session:
            memo = await self.memo_service.get(session, obj_id, context=context)
            if not memo:
                return None

            if obj_in.tags is not None:
                tags = await self.tag_service.get_or_create_tags(
                    session, obj_in.tags, context
                )
                memo.tags = tags

            update_data = obj_in.model_dump(exclude_unset=True, exclude={"tags"})
            if update_data:
                for field, value in update_data.items():
                    setattr(memo, field, value)

            session.add(memo)
            await session.flush()
            await session.refresh(memo)
            return memo


class DeleteMemoUseCase(BaseDeleteUseCase[MemoService, Memo, MemoContextKwargs]):
    def __init__(self, service: Annotated[MemoService, Depends()]) -> None:
        super().__init__(service)
