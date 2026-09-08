from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependencies import get_db
from app.database.models import UserModel
from app.schemas.api_response import ApiResponse
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):

    user = auth_service.register(db=db, request=request)

    return ApiResponse(
        message="User registered successfully.",
        data=user,
    )


@router.post("/login")
def login(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):

    token = auth_service.login(db=db, request=request)

    return ApiResponse(
        message="Login successful.",
        data=token,
    )


@router.get("/me")
def get_me(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):

    return ApiResponse(
        message="Current user retrieved successfully.",
        data=UserResponse.model_validate(current_user),
    )
