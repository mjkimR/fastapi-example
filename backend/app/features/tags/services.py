from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.services.base import BaseGetServiceMixin, BaseGetMultiServiceMixin
from app.base.services.nested_resource_hook import NestedResourceContextKwargs, NestedResourceHooksMixin
from app.features.tags.models import Tag
from app.features.tags.repos import TagRepository
from app.features.workspaces.repos import WorkspaceRepository


class TagService(
    NestedResourceHooksMixin,
    BaseGetMultiServiceMixin[TagRepository, Tag, NestedResourceContextKwargs],
    BaseGetServiceMixin[TagRepository, Tag, NestedResourceContextKwargs],
):
    """Service class for handling tag-related operations within a workspace."""

    def __init__(
            self,
            repo: Annotated[TagRepository, Depends()],
            parent_repo: Annotated[WorkspaceRepository, Depends()]
    ) -> None:
        self.repo: TagRepository = repo
        self.context_model = NestedResourceContextKwargs

        self.parent_repo = parent_repo
        self.fk_name = "workspace_id"

    async def get_or_create_tags(
            self,
            session: AsyncSession,
            tag_names: list[str],
            context: NestedResourceContextKwargs,
    ) -> list[Tag]:
        return await self.repo.get_or_create_tags(session, tag_names, workspace_id=context["parent_id"])
