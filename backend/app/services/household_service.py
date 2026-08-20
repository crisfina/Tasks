from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    ConflictError,
    ErrorCode,
    NotFoundError,
)
from app.enums.household_role import HouseholdRole
from app.models.household import Household
from app.models.household_user import HouseholdUser
from app.models.user import User
from app.schemas.household import (
    HouseholdCreate,
    HouseholdUpdate,
)
from app.schemas.household_user import (
    HouseholdUserCreate,
    HouseholdUserUpdate,
)
from app.services.user_service import get_user_or_raise


def get_household_by_id(
    db: Session,
    household_id: int,
    include_inactive: bool = False,
) -> Household | None:
    statement = select(Household).where(
        Household.id == household_id,
    )

    if not include_inactive:
        statement = statement.where(
            Household.is_active.is_(True),
        )

    return db.scalar(statement)


def get_household_or_raise(
    db: Session,
    household_id: int,
    include_inactive: bool = False,
) -> Household:
    household = get_household_by_id(
        db,
        household_id,
        include_inactive=include_inactive,
    )

    if household is None:
        raise NotFoundError(
            ErrorCode.HOUSEHOLD_NOT_FOUND,
        )

    return household


def get_membership(
    db: Session,
    household_id: int,
    user_id: int,
) -> HouseholdUser | None:
    statement = select(HouseholdUser).where(
        HouseholdUser.household_id == household_id,
        HouseholdUser.user_id == user_id,
    )

    return db.scalar(statement)


def get_membership_or_raise(
    db: Session,
    household_id: int,
    user_id: int,
) -> HouseholdUser:
    membership = get_membership(
        db,
        household_id,
        user_id,
    )

    if membership is None:
        raise NotFoundError(
            ErrorCode.HOUSEHOLD_MEMBER_NOT_FOUND,
        )

    return membership


def require_household_admin(
    db: Session,
    household_id: int,
    user_id: int,
) -> HouseholdUser:
    membership = get_membership(
        db,
        household_id,
        user_id,
    )

    if (
        membership is None
        or membership.role != HouseholdRole.ADMIN
    ):
        raise AuthorizationError(
            ErrorCode.HOUSEHOLD_ADMIN_REQUIRED,
        )

    return membership


def create_household(
    db: Session,
    data: HouseholdCreate,
    creator: User,
) -> Household:
    household = Household(
        name=data.name,
    )

    db.add(household)
    db.flush()

    membership = HouseholdUser(
        household_id=household.id,
        user_id=creator.id,
        role=HouseholdRole.ADMIN,
    )

    db.add(membership)
    db.commit()
    db.refresh(household)

    return household


def get_user_households(
    db: Session,
    user_id: int,
) -> list[Household]:
    statement = (
        select(Household)
        .join(HouseholdUser)
        .where(
            HouseholdUser.user_id == user_id,
            Household.is_active.is_(True),
        )
        .order_by(Household.name)
    )

    return list(db.scalars(statement).all())


def update_household(
    db: Session,
    household_id: int,
    actor_id: int,
    data: HouseholdUpdate,
) -> Household:
    household = get_household_or_raise(
        db,
        household_id,
    )

    require_household_admin(
        db,
        household_id,
        actor_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    for field, value in changes.items():
        setattr(household, field, value)

    db.commit()
    db.refresh(household)

    return household


def deactivate_household(
    db: Session,
    household_id: int,
    actor_id: int,
) -> None:
    household = get_household_or_raise(
        db,
        household_id,
    )

    require_household_admin(
        db,
        household_id,
        actor_id,
    )

    household.is_active = False
    db.commit()


def restore_household(
    db: Session,
    household_id: int,
    actor_id: int,
) -> Household:
    household = get_household_or_raise(
        db,
        household_id,
        include_inactive=True,
    )

    require_household_admin(
        db,
        household_id,
        actor_id,
    )

    household.is_active = True
    db.commit()
    db.refresh(household)

    return household


def add_household_member(
    db: Session,
    household_id: int,
    actor_id: int,
    data: HouseholdUserCreate,
) -> HouseholdUser:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_admin(
        db,
        household_id,
        actor_id,
    )

    get_user_or_raise(
        db,
        data.user_id,
    )

    existing_membership = get_membership(
        db,
        household_id,
        data.user_id,
    )

    if existing_membership is not None:
        raise ConflictError(
            ErrorCode.USER_ALREADY_HOUSEHOLD_MEMBER,
        )

    membership = HouseholdUser(
        household_id=household_id,
        user_id=data.user_id,
        role=data.role,
    )

    db.add(membership)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise ConflictError(
            ErrorCode.USER_ALREADY_HOUSEHOLD_MEMBER,
        ) from error

    db.refresh(membership)

    return membership


def _count_household_admins(
    db: Session,
    household_id: int,
) -> int:
    statement = (
        select(func.count())
        .select_from(HouseholdUser)
        .where(
            HouseholdUser.household_id == household_id,
            HouseholdUser.role == HouseholdRole.ADMIN,
        )
    )

    return db.scalar(statement) or 0


def update_household_member(
    db: Session,
    household_id: int,
    user_id: int,
    actor_id: int,
    data: HouseholdUserUpdate,
) -> HouseholdUser:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_admin(
        db,
        household_id,
        actor_id,
    )

    membership = get_membership_or_raise(
        db,
        household_id,
        user_id,
    )

    is_removing_admin_role = (
        membership.role == HouseholdRole.ADMIN
        and data.role != HouseholdRole.ADMIN
    )

    if (
        is_removing_admin_role
        and _count_household_admins(
            db,
            household_id,
        ) <= 1
    ):
        raise BusinessRuleError(
            ErrorCode.LAST_HOUSEHOLD_ADMIN,
        )

    membership.role = data.role

    db.commit()
    db.refresh(membership)

    return membership


def remove_household_member(
    db: Session,
    household_id: int,
    user_id: int,
    actor_id: int,
) -> None:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_admin(
        db,
        household_id,
        actor_id,
    )

    membership = get_membership_or_raise(
        db,
        household_id,
        user_id,
    )

    if (
        membership.role == HouseholdRole.ADMIN
        and _count_household_admins(
            db,
            household_id,
        ) <= 1
    ):
        raise BusinessRuleError(
            ErrorCode.LAST_HOUSEHOLD_ADMIN,
        )

    db.delete(membership)
    db.commit()