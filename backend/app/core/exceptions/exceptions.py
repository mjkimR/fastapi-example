from fastapi import status
from app.core.exceptions.base import CustomException


class BadRequestException(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad Request"


class IncorrectEmailOrPasswordException(BadRequestException):
    message = "Incorrect email or password"
    trace = False


class ForbiddenException(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Forbidden"


class InvalidCredentialsException(ForbiddenException):
    message = "Could not validate credentials"
    trace = False


class PermissionDeniedException(ForbiddenException):
    message = "The user doesn't have enough privileges"
    trace = False


class UserCantDeleteItselfException(ForbiddenException):
    message = "User can't delete itself"
    trace = False


class NotFoundException(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Not Found"
    trace = False


class UserNotFoundException(NotFoundException):
    message = "User not found"
    trace = False


class ConflictException(CustomException):
    status_code = status.HTTP_409_CONFLICT
    message = "Conflict"


class UserAlreadyExistsException(ConflictException):
    message = "The user with this username already exists in the system"
    trace = False
