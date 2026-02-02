from enum import Enum


class MemoEventType(str, Enum):
    CREATE = "MEMO_CREATED"
    UPDATE = "MEMO_UPDATED"
    DELETE = "MEMO_DELETED"
