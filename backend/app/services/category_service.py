from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    ErrorCode,
    NotFoundError,
)
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
    require_household_owner,
)


def get_category_by_id(
    db: Session,
    household_id: int,
    category_id: int,
    include_inactive: bool = False,
) -> Category | None:
    statement = select(Category).where(
        Category.id == category_id,
        Category.household_id == household_id,
    )

    if not include_inactive:
        statement = statement.where(
            Category.is_active.is_(True),
        )

    return db.scalar(statement)


def get_category_or_raise(
    db: Session,
    household_id: int,
    category_id: int,
    include_inactive: bool = False,
) -> Category:
    category = get_category_by_id(
        db,
        household_id,
        category_id,
        include_inactive=include_inactive,
    )

    if category is None:
        raise NotFoundError(
            ErrorCode.CATEGORY_NOT_FOUND,
        )

    return category


def get_household_categories(
    db: Session,
    household_id: int,
    actor_id: int,
) -> list[Category]:
    get_household_or_raise(
        db,
        household_id,
    )

    get_membership_or_raise(
        db,
        household_id,
        actor_id,
    )

    statement = (
        select(Category)
        .where(
            Category.household_id == household_id,
            Category.is_active.is_(True),
        )
        .order_by(
            Category.display_order.asc().nulls_last(),
            Category.name,
        )
    )

    return list(
        db.scalars(statement).all(),
    )


def _ensure_unique_category_name(
    db: Session,
    household_id: int,
    name: str,
    exclude_category_id: int | None = None,
) -> None:
    statement = select(Category).where(
        Category.household_id == household_id,
        func.lower(Category.name) == name.lower(),
    )

    if exclude_category_id is not None:
        statement = statement.where(
            Category.id != exclude_category_id,
        )

    existing_category = db.scalar(statement)

    if existing_category is not None:
        raise ConflictError(
            ErrorCode.CATEGORY_NAME_EXISTS,
        )


def create_category(
    db: Session,
    household_id: int,
    actor_id: int,
    data: CategoryCreate,
) -> Category:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    _ensure_unique_category_name(
        db,
        household_id,
        data.name,
    )

    category_data = data.model_dump(
        exclude_none=True,
    )

    category = Category(
        household_id=household_id,
        **category_data,
    )

    db.add(category)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(
            ErrorCode.CATEGORY_NAME_EXISTS,
        ) from error

    db.refresh(category)

    return category


def update_category(
    db: Session,
    household_id: int,
    category_id: int,
    actor_id: int,
    data: CategoryUpdate,
) -> Category:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    category = get_category_or_raise(
        db,
        household_id,
        category_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if "name" in changes:
        _ensure_unique_category_name(
            db,
            household_id,
            changes["name"],
            exclude_category_id=category.id,
        )

    for field, value in changes.items():
        setattr(category, field, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(
            ErrorCode.CATEGORY_NAME_EXISTS,
        ) from error

    db.refresh(category)

    return category


def deactivate_category(
    db: Session,
    household_id: int,
    category_id: int,
    actor_id: int,
) -> None:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    category = get_category_or_raise(
        db,
        household_id,
        category_id,
    )

    category.is_active = False
    db.commit()


def restore_category(
    db: Session,
    household_id: int,
    category_id: int,
    actor_id: int,
) -> Category:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    category = get_category_or_raise(
        db,
        household_id,
        category_id,
        include_inactive=True,
    )

    category.is_active = True

    db.commit()
    db.refresh(category)

    return category