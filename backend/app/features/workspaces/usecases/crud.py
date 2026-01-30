from typing import Annotated, Optional

from fastapi import Depends

from app.base.services.user_aware_hook import UserContextKwargs
from app.core.database.transaction import AsyncTransaction
from app.features.outbox.schemas import OutboxCreate
from app.features.outbox.services import OutboxService
from app.features.workspaces.enum import WORKSPACE_RES_NAME, WorkspaceEventType
from app.features.workspaces.models import Workspace
from app.features.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceNotificationPayload,
)
from app.base.services.base import BaseContextKwargs
from app.features.workspaces.services import WorkspaceService
from app.base.usecases.crud import (
    BaseGetUseCase,
    BaseGetMultiUseCase,
    BaseDeleteUseCase,
    BaseCreateUseCase,
    BaseUpdateUseCase,
)


class GetWorkspaceUseCase(
    BaseGetUseCase[WorkspaceService, Workspace, BaseContextKwargs]
):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class GetMultiWorkspaceUseCase(
    BaseGetMultiUseCase[WorkspaceService, Workspace, BaseContextKwargs]
):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class CreateWorkspaceUseCase(
    BaseCreateUseCase[WorkspaceService, Workspace, WorkspaceCreate, UserContextKwargs]
):
    def __init__(
        self,
        workspace_service: Annotated[WorkspaceService, Depends()],
        outbox_service: Annotated[OutboxService, Depends()],  # NEW dependency
    ) -> None:
        self.workspace_service = workspace_service
        self.outbox_service = outbox_service  # Store it

    async def execute(
        self, obj_in: WorkspaceCreate, context: Optional[BaseContextKwargs] = None
    ) -> Workspace:
        async with AsyncTransaction() as session:
            workspace = await self.workspace_service.create(
                session, obj_data=obj_in, context=context
            )
            await session.flush()

            # Create and add the outbox event in the same transaction
            event_data = OutboxCreate(
                aggregate_type=WORKSPACE_RES_NAME,
                aggregate_id=str(workspace.id),
                event_type=WorkspaceEventType.CREATE,
                payload=WorkspaceNotificationPayload.from_orm(
                    workspace, context.user_id, WorkspaceEventType.CREATE
                ),
            )
            await self.outbox_service.add_event(session, event_data)

            await session.refresh(workspace)
            return workspace


class UpdateWorkspaceUseCase(
    BaseUpdateUseCase[WorkspaceService, Workspace, UserContextKwargs]
):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class DeleteWorkspaceUseCase(
    BaseDeleteUseCase[WorkspaceService, Workspace, BaseContextKwargs]
):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)
