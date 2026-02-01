from typing import Annotated

from fastapi import Depends

from app_kit.base.services.user_aware_hook import UserContextKwargs
from app_kit.base.usecases.crud import (
    BaseCreateUseCase,
    BaseDeleteUseCase,
    BaseGetMultiUseCase,
    BaseGetUseCase,
    BaseUpdateUseCase,
)
from app.features.workspaces.models import Workspace
from app.features.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceUpdate,
)
from app.features.workspaces.services import WorkspaceService


class GetWorkspaceUseCase(BaseGetUseCase[WorkspaceService, Workspace, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class GetMultiWorkspaceUseCase(BaseGetMultiUseCase[WorkspaceService, Workspace, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class CreateWorkspaceUseCase(BaseCreateUseCase[WorkspaceService, Workspace, WorkspaceCreate, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class UpdateWorkspaceUseCase(BaseUpdateUseCase[WorkspaceService, Workspace, WorkspaceUpdate, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class DeleteWorkspaceUseCase(BaseDeleteUseCase[WorkspaceService, Workspace, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)
