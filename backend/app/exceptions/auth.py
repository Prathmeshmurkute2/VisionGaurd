from fastapi import status

from app.exceptions.base import AppException


class UserAlreadyExistsException(AppException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message="A user with this username or email already exists.",
            error_code="USER_ALREADY_EXISTS",
        )


class InvalidCredentialsException(AppException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid username or password.",
            error_code="INVALID_CREDENTIALS",
        )


class InvalidTokenException(AppException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Could not validate credentials.",
            error_code="INVALID_TOKEN",
        )


class UserNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message="User not found.",
            error_code="USER_NOT_FOUND",
        )
