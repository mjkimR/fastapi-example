import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func, UUID, Boolean, JSON

Base = declarative_base()


class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class AuditMixin:
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def mark_deleted(self):
        self.is_deleted = True
        self.deleted_at = func.now()


class TaggableMixin:
    tags = Column(JSON, nullable=True)

    def add_tag(self, tag: str):
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
