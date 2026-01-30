from typing import Optional

from fastapi import status


class CustomException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal Server Error"
    log_message = None
    trace = True

    def __init__(
        self,
        message: Optional[str] = None,
        log_message: Optional[str] = None,
        status_code: Optional[int] = None,
        trace: Optional[bool] = None,
    ):
        if message is not None:
            self.message = message
        if log_message is not None:
            self.log_message = log_message
        if status_code is not None:
            self.status_code = status_code
        if trace is not None:
            self.trace = trace

        if log_message is None:
            self.log_message = self.message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"

    def to_dict(self):
        return {
            "message": self.message,
            "log_message": self.log_message,
            "status_code": self.status_code,
        }
