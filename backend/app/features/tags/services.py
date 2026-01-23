from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tags.models import Tag
from app.features.tags.repos import TagRepository
from app.base.services.base import BaseGetMultiServiceMixin, BaseGetServiceMixin, BaseContextKwargs


class TagService(
    BaseGetServiceMixin[TagRepository, Tag, BaseContextKwargs],
    BaseGetMultiServiceMixin[TagRepository, Tag, BaseContextKwargs]
):
    """Service class for handling tag-related operations."""

    def __init__(self, repo: Annotated[TagRepository, Depends()]) -> None:
        self.repo = repo

    async def get_or_create_tags(self, session: AsyncSession, tag_names: list[str]) -> list[Tag]:
        return await self.repo.get_or_create_tags(session, tag_names)
