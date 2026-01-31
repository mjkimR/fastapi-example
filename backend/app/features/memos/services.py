from typing import Annotated, Any

from fastapi import Depends

from app.base.services.base import (
    BaseCreateServiceMixin,
    BaseGetMultiServiceMixin,
    BaseUpdateServiceMixin,
    BaseDeleteServiceMixin,
    BaseGetServiceMixin,
)
from app.base.services.detail_delete_response_hook import DetailDeleteResponseHookMixin
from app.base.services.exists_check_hook import ExistsCheckHooksMixin
from app.base.services.user_aware_hook import UserAwareHooksMixin, UserContextKwargs
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.base.services.nested_resource_hook import (
    NestedResourceContextKwargs,
    NestedResourceHooksMixin,
)
from app.features.notifications.service_hooks import NotificationOutboxHook
from app.features.outbox.repos import OutboxRepository
from app.features.workspaces.repos import WorkspaceRepository
from app.features.memos.models import Memo


class MemoContextKwargs(NestedResourceContextKwargs, UserContextKwargs):
    pass


class MemoService(
    NestedResourceHooksMixin,
    UserAwareHooksMixin,
    DetailDeleteResponseHookMixin,
    NotificationOutboxHook,
    ExistsCheckHooksMixin,
    BaseCreateServiceMixin[MemoRepository, Memo, MemoCreate, MemoContextKwargs],
    BaseGetMultiServiceMixin[MemoRepository, Memo, MemoContextKwargs],
    BaseGetServiceMixin[MemoRepository, Memo, MemoContextKwargs],
    BaseUpdateServiceMixin[MemoRepository, Memo, MemoUpdate, MemoContextKwargs],
    BaseDeleteServiceMixin[MemoRepository, Memo, MemoContextKwargs],
):
    """Service class for handling memo-related operations within a workspace."""

    def __init__(
        self,
        repo: Annotated[MemoRepository, Depends()],
        parent_repo: Annotated[WorkspaceRepository, Depends()],
        outbox_repo: Annotated[OutboxRepository, Depends()],
    ):
        self._repo = repo
        self._parent_repo = parent_repo
        self._outbox_repo = outbox_repo

    @property
    def repo(self) -> MemoRepository:
        return self._repo

    @property
    def parent_repo(self) -> WorkspaceRepository:
        return self._parent_repo

    @property
    def outbox_repo(self) -> OutboxRepository:
        return self._outbox_repo

    @property
    def context_model(self):
        return MemoContextKwargs

    @property
    def fk_name(self) -> str:
        return "workspace_id"

    @property
    def notification_event_type_dict(self) -> dict[str, str]:
        from app.features.memos.enum import MemoEventType

        return {
            "CREATE": MemoEventType.CREATE,
            "UPDATE": MemoEventType.UPDATE,
            "DELETE": MemoEventType.DELETE,
        }

    def _get_notification_payload(
        self, obj: Memo, context: MemoContextKwargs, outbox_identity: dict[str, str]
    ) -> dict[str, Any]:
        return {
            "id": str(obj.id),
            "workspace_id": str(obj.workspace_id),
            "user_id": str(context.get("user_id")),
            "title": obj.title,
            "event_type": outbox_identity["event_type"],
        }

    def _parse_delete_represent_text(self, obj: Memo) -> str:
        return obj.title
