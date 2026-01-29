from typing import Union, AsyncIterator, Tuple, Annotated
from fastapi import Depends
from sqlalchemy.sql.expression import ColumnElement

from app.base.services.exists_check_hook import ExistsCheckHooksMixin
from app.base.services.unique_constraints_hook import UniqueConstraintHooksMixin
from app.base.services.user_aware_hook import UserAwareHooksMixin, UserContextKwargs
from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app.base.services.base import (
    BaseCreateServiceMixin,
    BaseUpdateServiceMixin,
    BaseGetMultiServiceMixin,
    BaseGetServiceMixin,
    BaseDeleteServiceMixin,
)


class WorkspaceService(
    UniqueConstraintHooksMixin,
    UserAwareHooksMixin,
    ExistsCheckHooksMixin,
    BaseCreateServiceMixin[WorkspaceRepository, Workspace, WorkspaceCreate, UserContextKwargs],
    BaseUpdateServiceMixin[WorkspaceRepository, Workspace, WorkspaceUpdate, UserContextKwargs],
    BaseGetMultiServiceMixin[WorkspaceRepository, Workspace, UserContextKwargs],
    BaseGetServiceMixin[WorkspaceRepository, Workspace, UserContextKwargs],
    BaseDeleteServiceMixin[WorkspaceRepository, Workspace, UserContextKwargs],
):
    context_model = UserContextKwargs

    def __init__(self, repo: Annotated[WorkspaceRepository, Depends()]):
        self._repo = repo

    @property
    def repo(self) -> WorkspaceRepository:
        return self._repo

    async def _unique_constraints(
            self,
            obj_data: Union[WorkspaceCreate, WorkspaceUpdate],
            context: UserContextKwargs
    ) -> AsyncIterator[Tuple[ColumnElement[bool], str]]:
        if obj_data.name:
            yield Workspace.name == obj_data.name, "Workspace with this name already exists."
