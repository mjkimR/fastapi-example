from typing import Annotated

from fastapi import Depends

from app.base.services.base import BaseCreateServiceMixin, BaseGetMultiServiceMixin, BaseUpdateServiceMixin, BaseDeleteServiceMixin, BaseGetServiceMixin
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

    def __init__(
            self,
            repo: Annotated[MemoRepository, Depends()],
            parent_repo: Annotated[WorkspaceRepository, Depends()]
    ):
        self.repo = repo
        self.context_model = MemoContextKwargs

        self.parent_repo = parent_repo
        self.fk_name = "workspace_id"
