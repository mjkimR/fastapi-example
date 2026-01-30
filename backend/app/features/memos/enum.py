from enum import Enum

MEMO_RES_NAME = "memo"


class MemoEventType(Enum, str):
    CREATE = "MEMO_CREATED"
    UPDATE = "MEMO_UPDATED"
    DELETE = "MEMO_DELETED"
