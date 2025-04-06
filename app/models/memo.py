from sqlalchemy import Column, String

from models.base import (Base, UUIDMixin, TimestampMixin)


class Memo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memos"

    category = Column(String, index=True)
    title = Column(String)
    contents = Column(String)
