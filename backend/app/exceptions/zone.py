from fastapi import status

from app.exceptions.base import AppException


class ZoneNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Zone not found.",
            error_code="ZONE_NOT_FOUND",
        )
