import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app_base.base.repos.base import BaseRepository
from app.features.tags.models import Tag
from app.features.tags.schemas import TagCreate, TagUpdate


class TagRepository(BaseRepository[Tag, TagCreate, TagUpdate]):
    model = Tag

    async def get_or_create_tags(
        self, session: AsyncSession, tag_names: list[str], workspace_id: uuid.UUID
    ) -> list[Tag]:
        """Get existing tags or create new ones for the given names within a workspace."""
        if not tag_names:
            return []

        # Find existing tags within the workspace
        stmt = select(self.model).where(and_(self.model.name.in_(tag_names), self.model.workspace_id == workspace_id))
        result = await session.execute(stmt)
        existing_tags = result.scalars().all()
        existing_tag_names = {tag.name for tag in existing_tags}

        # Determine which tags are new
        new_tag_names = set(tag_names) - existing_tag_names

        # Create new tags
        new_tags = []
        if new_tag_names:
            new_tags = [self.model(name=name, workspace_id=workspace_id) for name in new_tag_names]
            session.add_all(new_tags)
            await session.flush()

        return list(existing_tags) + new_tags
