from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenRead
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    authenticate_user,
    create_token_response,
)
from app.services.user_service import create_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:
    return create_user(
        db,
        data,
    )


@router.post(
    "/login",
    response_model=TokenRead,
)
def login(
    data: LoginRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> TokenRead:
    user = authenticate_user(
        db,
        data,
    )

    return create_token_response(
        user,
        data,
    )

@router.get(
    "/me",
    response_model=UserRead,
)
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    return current_user