from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.core.dependencies import get_db
from app.database.models import UserModel
from app.exceptions.auth import InvalidTokenException
from app.repositories.user_repository import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel:
    """
    Decodes the JWT bearer token and loads the corresponding user.
    Raises InvalidTokenException if the token is missing, expired,
    or does not match a known user.
    """

    payload = decode_access_token(token)

    if payload is None:
        raise InvalidTokenException()

    username = payload.get("sub")

    if username is None:
        raise InvalidTokenException()

    user = user_repository.get_by_username(db, username)

    if user is None:
        raise InvalidTokenException()

    return user


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-gated routes, e.g.:

        @router.delete("/cameras/{id}")
        def delete_camera(
            user: Annotated[UserModel, Depends(require_role("admin"))],
        ):
            ...
    """

    def dependency(
        user: Annotated[UserModel, Depends(get_current_user)],
    ) -> UserModel:

        if user.role not in allowed_roles:
            raise InvalidTokenException()

        return user

    return dependency
