from datetime import UTC, datetime, timedelta
from hashlib import sha256
import secrets

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
from app.models.household_invitation import HouseholdInvitation
from app.models.household_user import HouseholdUser
from app.models.user import User
from app.schemas.household import (
    HouseholdCreate,
    HouseholdUpdate,
)
from app.schemas.household_invitation import (
    HouseholdInvitationAccept,
    HouseholdInvitationCreate,
)
from app.schemas.household_user import (
    HouseholdUserCreate,
    HouseholdUserUpdate,
)
from app.services.user_service import get_user_or_raise


INVITATION_EXPIRATION_DAYS = 7


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


def require_household_owner(
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
        or membership.role != HouseholdRole.OWNER
    ):
        raise AuthorizationError(
            ErrorCode.HOUSEHOLD_OWNER_REQUIRED,
        )

    return membership


def require_household_manager(
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
        or membership.role not in (
            HouseholdRole.OWNER,
            HouseholdRole.MANAGER,
        )
    ):
        raise AuthorizationError(
            ErrorCode.HOUSEHOLD_MANAGER_REQUIRED,
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
        role=HouseholdRole.OWNER,
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
        .order_by(
            Household.name,
            Household.id,
        )
    )

    return list(
        db.scalars(statement).all(),
    )


def get_household_members(
    db: Session,
    household_id: int,
    actor_id: int,
) -> list[HouseholdUser]:
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
        select(HouseholdUser)
        .where(
            HouseholdUser.household_id == household_id,
        )
        .order_by(
            HouseholdUser.joined_at,
            HouseholdUser.user_id,
        )
    )

    return list(
        db.scalars(statement).all(),
    )


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

    require_household_owner(
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

    require_household_owner(
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

    require_household_owner(
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

    require_household_owner(
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


def _count_household_owners(
    db: Session,
    household_id: int,
) -> int:
    statement = (
        select(func.count())
        .select_from(HouseholdUser)
        .where(
            HouseholdUser.household_id == household_id,
            HouseholdUser.role == HouseholdRole.OWNER,
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

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    membership = get_membership_or_raise(
        db,
        household_id,
        user_id,
    )

    is_removing_owner_role = (
        membership.role == HouseholdRole.OWNER
        and data.role != HouseholdRole.OWNER
    )

    if (
        is_removing_owner_role
        and _count_household_owners(
            db,
            household_id,
        ) <= 1
    ):
        raise BusinessRuleError(
            ErrorCode.LAST_HOUSEHOLD_OWNER,
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

    require_household_owner(
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
        membership.role == HouseholdRole.OWNER
        and _count_household_owners(
            db,
            household_id,
        ) <= 1
    ):
        raise BusinessRuleError(
            ErrorCode.LAST_HOUSEHOLD_OWNER,
        )

    db.delete(membership)
    db.commit()


def _normalize_invitation_code(
    code: str,
) -> str:
    return code.replace("-", "").replace(" ", "").upper()


def _hash_invitation_code(
    code: str,
) -> str:
    normalized_code = _normalize_invitation_code(code)

    return sha256(
        normalized_code.encode("utf-8"),
    ).hexdigest()


def _generate_invitation_code() -> str:
    raw_code = secrets.token_hex(10).upper()

    return "-".join(
        (
            raw_code[0:5],
            raw_code[5:10],
            raw_code[10:15],
            raw_code[15:20],
        ),
    )


def create_household_invitation(
    db: Session,
    household_id: int,
    actor_id: int,
    data: HouseholdInvitationCreate,
) -> tuple[HouseholdInvitation, str]:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    code = _generate_invitation_code()

    invitation = HouseholdInvitation(
        household_id=household_id,
        created_by_user_id=actor_id,
        role=data.role,
        code_hash=_hash_invitation_code(code),
        expires_at=datetime.now(UTC) + timedelta(
            days=INVITATION_EXPIRATION_DAYS,
        ),
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation, code


def accept_household_invitation(
    db: Session,
    actor_id: int,
    data: HouseholdInvitationAccept,
) -> HouseholdUser:
    code_hash = _hash_invitation_code(data.code)

    statement = (
        select(HouseholdInvitation)
        .where(
            HouseholdInvitation.code_hash == code_hash,
        )
        .with_for_update()
    )

    invitation = db.scalar(statement)

    if invitation is None:
        raise NotFoundError(
            ErrorCode.HOUSEHOLD_INVITATION_NOT_FOUND,
        )

    if invitation.revoked_at is not None:
        raise BusinessRuleError(
            ErrorCode.HOUSEHOLD_INVITATION_REVOKED,
        )

    if invitation.accepted_at is not None:
        raise ConflictError(
            ErrorCode.HOUSEHOLD_INVITATION_ALREADY_ACCEPTED,
        )

    if invitation.expires_at <= datetime.now(UTC):
        raise BusinessRuleError(
            ErrorCode.HOUSEHOLD_INVITATION_EXPIRED,
        )

    existing_membership = get_membership(
        db,
        invitation.household_id,
        actor_id,
    )

    if existing_membership is not None:
        raise ConflictError(
            ErrorCode.USER_ALREADY_HOUSEHOLD_MEMBER,
        )

    membership = HouseholdUser(
        household_id=invitation.household_id,
        user_id=actor_id,
        role=invitation.role,
    )

    invitation.accepted_by_user_id = actor_id
    invitation.accepted_at = datetime.now(UTC)

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