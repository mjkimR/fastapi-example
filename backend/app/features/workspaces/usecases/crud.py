from typing import Annotated

from fastapi import Depends

from app.base.services.user_aware_hook import UserContextKwargs
from app.features.workspaces.models import Workspace
from app.features.workspaces.schemas import WorkspaceCreate
from app.base.services.base import BaseContextKwargs
from app.features.workspaces.services import WorkspaceService
from app.base.usecases.crud import (
    BaseGetUseCase,
    BaseGetMultiUseCase,
    BaseDeleteUseCase, BaseCreateUseCase, BaseUpdateUseCase,
)


class GetWorkspaceUseCase(BaseGetUseCase[WorkspaceService, Workspace, BaseContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class GetMultiWorkspaceUseCase(BaseGetMultiUseCase[WorkspaceService, Workspace, BaseContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class CreateWorkspaceUseCase(BaseCreateUseCase[WorkspaceService, Workspace, WorkspaceCreate, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class UpdateWorkspaceUseCase(BaseUpdateUseCase[WorkspaceService, Workspace, UserContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)


class DeleteWorkspaceUseCase(BaseDeleteUseCase[WorkspaceService, Workspace, BaseContextKwargs]):
    def __init__(self, service: Annotated[WorkspaceService, Depends()]) -> None:
        super().__init__(service)
