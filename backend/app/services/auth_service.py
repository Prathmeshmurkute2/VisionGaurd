from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.exceptions.auth import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.auth import UserResponse


class AuthService:

    def register(self, db: Session, request: RegisterRequest):

        existing_user = user_repository.get_by_username(
            db, request.username
        )

        if existing_user is not None:
            raise UserAlreadyExistsException()

        existing_email = user_repository.get_by_email(
            db, request.email
        )

        if existing_email is not None:
            raise UserAlreadyExistsException()

        db_user = user_repository.create(
            db=db,
            username=request.username,
            email=request.email,
            password_hash=hash_password(request.password),
            role=request.role,
        )

        return UserResponse.model_validate(db_user)

    def login(self, db: Session, request: LoginRequest) -> TokenResponse:

        db_user = user_repository.get_by_username(
            db, request.username
        )

        if db_user is None:
            raise InvalidCredentialsException()

        if not verify_password(request.password, db_user.password_hash):
            raise InvalidCredentialsException()

        access_token = create_access_token(
            data={"sub": db_user.username, "role": db_user.role}
        )

        return TokenResponse(access_token=access_token)


auth_service = AuthService()
