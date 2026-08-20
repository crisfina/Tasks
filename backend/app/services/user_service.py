from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    ErrorCode,
    NotFoundError,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserPasswordUpdate,
    UserUpdate,
    UserUpdateAdmin,
)


def get_user_by_id(
    db: Session,
    user_id: int,
    include_inactive: bool = False,
) -> User | None:
    statement = select(User).where(
        User.id == user_id,
    )

    if not include_inactive:
        statement = statement.where(
            User.is_active.is_(True),
        )

    return db.scalar(statement)


def get_user_or_raise(
    db: Session,
    user_id: int,
    include_inactive: bool = False,
) -> User:
    user = get_user_by_id(
        db,
        user_id,
        include_inactive=include_inactive,
    )

    if user is None:
        raise NotFoundError(
            ErrorCode.USER_NOT_FOUND,
        )

    return user


def get_user_by_identifier(
    db: Session,
    identifier: str,
) -> User | None:
    normalized_identifier = identifier.strip().lower()

    statement = select(User).where(
        or_(
            func.lower(User.username) == normalized_identifier,
            func.lower(User.email) == normalized_identifier,
        ),
        User.is_active.is_(True),
    )

    return db.scalar(statement)


def _ensure_unique_user_fields(
    db: Session,
    username: str | None = None,
    email: str | None = None,
    exclude_user_id: int | None = None,
) -> None:
    conditions = []

    if username is not None:
        conditions.append(
            func.lower(User.username) == username.lower(),
        )

    if email is not None:
        conditions.append(
            func.lower(User.email) == email.lower(),
        )

    if not conditions:
        return

    statement = select(User).where(
        or_(*conditions),
    )

    if exclude_user_id is not None:
        statement = statement.where(
            User.id != exclude_user_id,
        )

    existing_user = db.scalar(statement)

    if existing_user is not None:
        raise ConflictError(
            ErrorCode.USERNAME_OR_EMAIL_EXISTS,
        )


def create_user(
    db: Session,
    data: UserCreate,
) -> User:
    _ensure_unique_user_fields(
        db,
        username=data.username,
        email=str(data.email),
    )

    user_data = data.model_dump(
        exclude={"password"},
        exclude_none=True,
    )

    user_data["email"] = str(data.email).lower()

    user = User(
        **user_data,
        password_hash=hash_password(data.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise ConflictError(
            ErrorCode.USERNAME_OR_EMAIL_EXISTS,
        ) from error

    db.refresh(user)

    return user


def update_user(
    db: Session,
    user: User,
    data: UserUpdate,
) -> User:
    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    _ensure_unique_user_fields(
        db,
        username=changes.get("username"),
        email=changes.get("email"),
        exclude_user_id=user.id,
    )

    if "email" in changes:
        changes["email"] = str(
            changes["email"]
        ).lower()

    for field, value in changes.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise ConflictError(
            ErrorCode.USERNAME_OR_EMAIL_EXISTS,
        ) from error

    db.refresh(user)

    return user


def update_user_admin(
    db: Session,
    user: User,
    data: UserUpdateAdmin,
) -> User:
    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    _ensure_unique_user_fields(
        db,
        username=changes.get("username"),
        email=changes.get("email"),
        exclude_user_id=user.id,
    )

    if "email" in changes:
        changes["email"] = str(
            changes["email"]
        ).lower()

    for field, value in changes.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise ConflictError(
            ErrorCode.USERNAME_OR_EMAIL_EXISTS,
        ) from error

    db.refresh(user)

    return user


def change_password(
    db: Session,
    user: User,
    data: UserPasswordUpdate,
) -> None:
    if not verify_password(
        data.current_password,
        user.password_hash,
    ):
        raise AuthenticationError(
            ErrorCode.INVALID_CURRENT_PASSWORD,
        )

    user.password_hash = hash_password(
        data.new_password,
    )

    db.commit()


def deactivate_user(
    db: Session,
    user: User,
    password: str,
) -> None:
    if not verify_password(
        password,
        user.password_hash,
    ):
        raise AuthenticationError(
            ErrorCode.INVALID_PASSWORD,
        )

    user.is_active = False

    db.commit()


def reactivate_user(
    db: Session,
    user: User,
) -> User:
    user.is_active = True

    db.commit()
    db.refresh(user)

    return user