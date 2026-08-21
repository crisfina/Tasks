from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ErrorCode,
)
from app.core.security import decode_access_token
from app.db.database import get_db
from app.enums.user_role import UserRole
from app.models.user import User
from app.services.user_service import get_user_by_id


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:
    user_id = decode_access_token(
        credentials.credentials,
    )

    if user_id is None:
        raise AuthenticationError(
            ErrorCode.INVALID_TOKEN,
        )

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise AuthenticationError(
            ErrorCode.INVALID_TOKEN,
        )

    return user


def get_current_admin(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError(
            ErrorCode.ADMIN_REQUIRED,
        )

    return current_user