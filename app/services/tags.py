from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tags import Tag
from app.repos.tags import TagRepository
from app.services.base.basic import BasicGetMultiServiceMixin, BasicGetServiceMixin


class TagService(
    BasicGetServiceMixin[TagRepository, Tag],
    BasicGetMultiServiceMixin[TagRepository, Tag]
):
    """Service class for handling tag-related operations."""

    def __init__(self, repo: Annotated[TagRepository, Depends()]) -> None:
        self.repo = repo

    async def get_or_create_tags(self, session: AsyncSession, tag_names: list[str]) -> list[Tag]:
        return await self.repo.get_or_create_tags(session, tag_names)
