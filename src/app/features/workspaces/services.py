from typing import Annotated, Any, AsyncIterator, Tuple, Union

from fastapi import Depends
from sqlalchemy.sql.expression import ColumnElement

from app.features.notifications.service_hooks import (
    NotificationOutboxHook,
)
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.schemas import OutboxIdentityDict
from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app_base.base.services.base import (
    BaseCreateServiceMixin,
    BaseDeleteServiceMixin,
    BaseGetMultiServiceMixin,
    BaseGetServiceMixin,
    BaseUpdateServiceMixin,
    TContextKwargs,
)
from app_base.base.services.detail_delete_response_hook import DetailDeleteResponseHookMixin
from app_base.base.services.exists_check_hook import ExistsCheckHooksMixin
from app_base.base.services.unique_constraints_hook import UniqueConstraintHooksMixin
from app_base.base.services.user_aware_hook import UserAwareHooksMixin, UserContextKwargs


class WorkspaceService(
    UniqueConstraintHooksMixin,  # Ensure unique constraints before create/update
    UserAwareHooksMixin,  # Add created_by and updated_by handling
    DetailDeleteResponseHookMixin,  # Provide detailed response on delete (represent text)
    NotificationOutboxHook,  # Add notification outbox item on create, update, delete
    ExistsCheckHooksMixin,  # Ensure existence checks before operations
    BaseCreateServiceMixin[WorkspaceRepository, Workspace, WorkspaceCreate, UserContextKwargs],
    BaseUpdateServiceMixin[WorkspaceRepository, Workspace, WorkspaceUpdate, UserContextKwargs],
    BaseGetMultiServiceMixin[WorkspaceRepository, Workspace, UserContextKwargs],
    BaseGetServiceMixin[WorkspaceRepository, Workspace, UserContextKwargs],
    BaseDeleteServiceMixin[WorkspaceRepository, Workspace, UserContextKwargs],
):
    def __init__(
        self,
        repo: Annotated[WorkspaceRepository, Depends()],
        outbox_repo: Annotated[OutboxRepository, Depends()],
    ):
        self._repo = repo
        self._outbox_repo = outbox_repo

    @property
    def repo(self) -> WorkspaceRepository:
        return self._repo

    @property
    def outbox_repo(self) -> OutboxRepository:
        return self._outbox_repo

    @property
    def context_model(self):
        return UserContextKwargs

    @property
    def notification_event_type_dict(self) -> dict[str, str]:
        from app.features.workspaces.enum import WorkspaceEventType

        return {
            "CREATE": WorkspaceEventType.CREATE,
            "UPDATE": WorkspaceEventType.UPDATE,
            "DELETE": WorkspaceEventType.DELETE,
        }

    def _get_notification_payload(
        self, obj: Any, context: TContextKwargs, outbox_identity: OutboxIdentityDict
    ) -> dict[str, Any]:
        return {
            "id": str(obj.id),
            "name": obj.name,
            "user_id": str(context.get("user_id")),
            "event_type": outbox_identity["event_type"],
        }

    def _parse_delete_represent_text(self, obj: Any) -> str:
        return obj.name

    async def _unique_constraints(
        self,
        obj_data: Union[WorkspaceCreate, WorkspaceUpdate],
        context: UserContextKwargs,
    ) -> AsyncIterator[Tuple[ColumnElement[bool], str]]:
        if obj_data.name:
            yield Workspace.name == obj_data.name, "Workspace with this name already exists."
