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


def get_household_category_by_id(
    db: Session,
    household_id: int,
    category_id: int,
    include_inactive: bool = False,
) -> Category | None:
    statement = select(Category).where(
        Category.id == category_id,
        Category.household_id == household_id,
        Category.user_id.is_(None),
    )

    if not include_inactive:
        statement = statement.where(
            Category.is_active.is_(True),
        )

    return db.scalar(statement)


def get_household_category_or_raise(
    db: Session,
    household_id: int,
    category_id: int,
    include_inactive: bool = False,
) -> Category:
    category = get_household_category_by_id(
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


def get_personal_category_by_id(
    db: Session,
    user_id: int,
    category_id: int,
    include_inactive: bool = False,
) -> Category | None:
    statement = select(Category).where(
        Category.id == category_id,
        Category.user_id == user_id,
        Category.household_id.is_(None),
    )

    if not include_inactive:
        statement = statement.where(
            Category.is_active.is_(True),
        )

    return db.scalar(statement)


def get_personal_category_or_raise(
    db: Session,
    user_id: int,
    category_id: int,
    include_inactive: bool = False,
) -> Category:
    category = get_personal_category_by_id(
        db,
        user_id,
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
            Category.user_id.is_(None),
            Category.is_active.is_(True),
        )
        .order_by(
            Category.display_order.asc().nulls_last(),
            Category.name,
            Category.id,
        )
    )

    return list(
        db.scalars(statement).all(),
    )


def get_personal_categories(
    db: Session,
    user_id: int,
) -> list[Category]:
    statement = (
        select(Category)
        .where(
            Category.user_id == user_id,
            Category.household_id.is_(None),
            Category.is_active.is_(True),
        )
        .order_by(
            Category.display_order.asc().nulls_last(),
            Category.name,
            Category.id,
        )
    )

    return list(
        db.scalars(statement).all(),
    )


def _ensure_unique_category_name(
    db: Session,
    name: str,
    household_id: int | None = None,
    user_id: int | None = None,
    exclude_category_id: int | None = None,
) -> None:
    statement = select(Category).where(
        func.lower(Category.name) == name.lower(),
    )

    if household_id is not None:
        statement = statement.where(
            Category.household_id == household_id,
            Category.user_id.is_(None),
        )
    else:
        statement = statement.where(
            Category.user_id == user_id,
            Category.household_id.is_(None),
        )

    if exclude_category_id is not None:
        statement = statement.where(
            Category.id != exclude_category_id,
        )

    if db.scalar(statement) is not None:
        raise ConflictError(
            ErrorCode.CATEGORY_NAME_EXISTS,
        )


def _commit_category(
    db: Session,
    category: Category,
) -> Category:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(
            ErrorCode.CATEGORY_NAME_EXISTS,
        ) from error

    db.refresh(category)
    return category


def create_household_category(
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
        data.name,
        household_id=household_id,
    )

    category = Category(
        household_id=household_id,
        user_id=None,
        **data.model_dump(
            exclude_none=True,
        ),
    )

    db.add(category)
    return _commit_category(
        db,
        category,
    )


def create_personal_category(
    db: Session,
    user_id: int,
    data: CategoryCreate,
) -> Category:
    _ensure_unique_category_name(
        db,
        data.name,
        user_id=user_id,
    )

    category = Category(
        household_id=None,
        user_id=user_id,
        **data.model_dump(
            exclude_none=True,
        ),
    )

    db.add(category)
    return _commit_category(
        db,
        category,
    )


def _apply_category_update(
    db: Session,
    category: Category,
    data: CategoryUpdate,
) -> Category:
    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if "name" in changes:
        _ensure_unique_category_name(
            db,
            changes["name"],
            household_id=category.household_id,
            user_id=category.user_id,
            exclude_category_id=category.id,
        )

    for field, value in changes.items():
        setattr(category, field, value)

    return _commit_category(
        db,
        category,
    )


def update_household_category(
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

    category = get_household_category_or_raise(
        db,
        household_id,
        category_id,
    )

    return _apply_category_update(
        db,
        category,
        data,
    )


def update_personal_category(
    db: Session,
    user_id: int,
    category_id: int,
    data: CategoryUpdate,
) -> Category:
    category = get_personal_category_or_raise(
        db,
        user_id,
        category_id,
    )

    return _apply_category_update(
        db,
        category,
        data,
    )


def deactivate_household_category(
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

    category = get_household_category_or_raise(
        db,
        household_id,
        category_id,
    )

    category.is_active = False
    db.commit()


def deactivate_personal_category(
    db: Session,
    user_id: int,
    category_id: int,
) -> None:
    category = get_personal_category_or_raise(
        db,
        user_id,
        category_id,
    )

    category.is_active = False
    db.commit()


def restore_household_category(
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

    category = get_household_category_or_raise(
        db,
        household_id,
        category_id,
        include_inactive=True,
    )

    category.is_active = True
    db.commit()
    db.refresh(category)

    return category


def restore_personal_category(
    db: Session,
    user_id: int,
    category_id: int,
) -> Category:
    category = get_personal_category_or_raise(
        db,
        user_id,
        category_id,
        include_inactive=True,
    )

    category.is_active = True
    db.commit()
    db.refresh(category)

    return category