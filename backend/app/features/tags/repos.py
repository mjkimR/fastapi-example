from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tags.models import Tag
from app.base.repos.base import BaseRepository


class TagRepository(BaseRepository[Tag, Tag, Tag]):
    model = Tag

    async def get_or_create_tags(self, session: AsyncSession, tag_names: list[str]) -> list[Tag]:
        """Get existing tags or create new ones for the given names."""
        if not tag_names:
            return []

        # Find existing tags
        stmt = select(self.model).where(self.model.name.in_(tag_names))
        result = await session.execute(stmt)
        existing_tags = result.scalars().all()
        existing_tag_names = {tag.name for tag in existing_tags}

        # Determine which tags are new
        new_tag_names = set(tag_names) - existing_tag_names

        # Create new tags
        new_tags = []
        if new_tag_names:
            new_tags = [self.model(name=name) for name in new_tag_names]
            session.add_all(new_tags)
            await session.flush()  # Flush to get IDs if needed elsewhere, though not strictly necessary here

        return list(existing_tags) + new_tags
