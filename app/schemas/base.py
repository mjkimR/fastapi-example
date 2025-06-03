import uuid
from datetime import datetime
from typing import Optional, List, Generic, TypeVar, Any, Sequence
from pydantic import BaseModel, computed_field


class UUIDSchemaMixin(BaseModel):
    id: uuid.UUID


class TimestampSchemaMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class AuditSchemaMixin(BaseModel):
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None


class SoftDeleteSchemaMixin(BaseModel):
    is_deleted: bool
    deleted_at: Optional[datetime] = None


class TaggableSchemaMixin(BaseModel):
    tags: Optional[List[str]] = None


PageItem = TypeVar('PageItem', bound=Any)


class PaginatedList(BaseModel, Generic[PageItem]):
    """Offset Pagination Items"""
    items: Sequence[PageItem]
    total_count: Optional[int] = None
    offset: int = 0
    limit: Optional[int] = None

    @computed_field
    @property
    def last(self) -> bool | None:
        """Check if the current page is the last page"""
        if self.limit is None or self.total_count is None:
            return None
        return self.offset + self.limit >= self.total_count

    @computed_field
    @property
    def first(self) -> bool:
        return self.offset == 0
