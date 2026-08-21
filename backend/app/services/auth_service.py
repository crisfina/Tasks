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
) -> TokenRead:
    access_token = create_access_token(
        user.id,
    )

    return TokenRead(
        access_token=access_token,
        expires_in=(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
    )