from typing import Annotated

from fastapi import Depends

from app.base.services.base import BaseCreateServiceMixin, BaseGetMultiServiceMixin, BaseUpdateServiceMixin, BaseDeleteServiceMixin, BaseGetServiceMixin, TRepo
from app.base.services.exists_check_hook import ExistsCheckHooksMixin
from app.base.services.user_aware_hook import UserAwareHooksMixin, UserContextKwargs
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.base.services.nested_resource_hook import NestedResourceContextKwargs, NestedResourceHooksMixin
from app.features.workspaces.repos import WorkspaceRepository
from app.features.memos.models import Memo


class MemoContextKwargs(NestedResourceContextKwargs, UserContextKwargs):
    pass


class MemoService(
    NestedResourceHooksMixin,
    UserAwareHooksMixin,
    ExistsCheckHooksMixin,
    BaseCreateServiceMixin[MemoRepository, Memo, MemoCreate, MemoContextKwargs],
    BaseGetMultiServiceMixin[MemoRepository, Memo, MemoContextKwargs],
    BaseGetServiceMixin[MemoRepository, Memo, MemoContextKwargs],
    BaseUpdateServiceMixin[MemoRepository, Memo, MemoUpdate, MemoContextKwargs],
    BaseDeleteServiceMixin[MemoRepository, Memo, MemoContextKwargs],
):
    """Service class for handling memo-related operations within a workspace."""
    context_model = MemoContextKwargs
    fk_name = "workspace_id"

    def __init__(
            self,
            repo: Annotated[MemoRepository, Depends()],
            parent_repo: Annotated[WorkspaceRepository, Depends()]
    ):
        self._repo = repo
        self._parent_repo = parent_repo

    @property
    def repo(self) -> MemoRepository:
        return self._repo

    @property
    def parent_repo(self) -> WorkspaceRepository:
        return self._parent_repo
