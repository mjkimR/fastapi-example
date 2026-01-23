from fastapi import status
from app.base.exceptions.base import CustomException


class BadRequestException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad Request"


class ForbiddenException(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Forbidden"


class NotFoundException(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Not Found"
    trace = False


class ConflictException(CustomException):
    status_code = status.HTTP_409_CONFLICT
    message = "Conflict"
