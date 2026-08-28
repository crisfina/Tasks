from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ErrorCode,
)
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenRead
from app.services.user_service import (
    get_user_by_identifier,
)


def authenticate_user(
    db: Session,
    data: LoginRequest,
) -> User:
    user = get_user_by_identifier(
        db,
        data.identifier,
    )

    if user is None:
        raise AuthenticationError(
            ErrorCode.INVALID_PASSWORD,
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise AuthenticationError(
            ErrorCode.INVALID_PASSWORD,
        )

    return user


def create_token_response(
    user: User,
    data: LoginRequest,
) -> TokenRead:
    expiration_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    if data.remember_me:
        expiration_minutes = (
            settings.REMEMBER_ME_TOKEN_EXPIRE_DAYS
            * 24
            * 60
        )

    access_token = create_access_token(
        user.id,
        expiration_minutes,
    )

    return TokenRead(
        access_token=access_token,
        expires_in=expiration_minutes * 60,
    )