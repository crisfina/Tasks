from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusinessRuleError,
    ErrorCode,
    NotFoundError,
)
from app.enums.point_scope import PointScope
from app.models.event import Event
from app.models.household import Household
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate


def get_event_by_id(
    db: Session,
    event_id: int,
    include_inactive: bool = False,
) -> Event | None:
    statement = select(Event).where(
        Event.id == event_id,
    )

    if not include_inactive:
        statement = statement.where(
            Event.is_active.is_(True),
        )

    return db.scalar(statement)


def get_event_or_raise(
    db: Session,
    event_id: int,
    include_inactive: bool = False,
) -> Event:
    event = get_event_by_id(
        db,
        event_id,
        include_inactive=include_inactive,
    )

    if event is None:
        raise NotFoundError(
            ErrorCode.EVENT_NOT_FOUND,
        )

    return event


def get_events(
    db: Session,
    scope: PointScope,
    household_id: int | None = None,
    user_id: int | None = None,
    include_inactive: bool = False,
) -> list[Event]:
    _validate_scope(
        scope,
        household_id,
        user_id,
    )

    statement = select(Event).where(
        Event.scope == scope,
    )

    if scope == PointScope.HOUSEHOLD:
        statement = statement.where(
            Event.household_id == household_id,
        )

    if scope == PointScope.PERSONAL:
        statement = statement.where(
            Event.user_id == user_id,
        )

    if not include_inactive:
        statement = statement.where(
            Event.is_active.is_(True),
        )

    statement = statement.order_by(
        Event.name,
        Event.id,
    )

    return list(
        db.scalars(statement).all(),
    )


def _validate_scope(
    scope: PointScope,
    household_id: int | None,
    user_id: int | None,
) -> None:
    if (
        scope == PointScope.HOUSEHOLD
        and (
            household_id is None
            or user_id is not None
        )
    ):
        raise BusinessRuleError(
            ErrorCode.EVENT_SCOPE_INVALID,
        )

    if (
        scope == PointScope.PERSONAL
        and (
            user_id is None
            or household_id is not None
        )
    ):
        raise BusinessRuleError(
            ErrorCode.EVENT_SCOPE_INVALID,
        )


def _validate_household(
    db: Session,
    household_id: int,
) -> None:
    statement = select(Household.id).where(
        Household.id == household_id,
        Household.is_active.is_(True),
    )

    if db.scalar(statement) is None:
        raise BusinessRuleError(
            ErrorCode.EVENT_HOUSEHOLD_INVALID,
        )


def _validate_user(
    db: Session,
    user_id: int,
) -> None:
    statement = select(User.id).where(
        User.id == user_id,
        User.is_active.is_(True),
    )

    if db.scalar(statement) is None:
        raise BusinessRuleError(
            ErrorCode.EVENT_USER_INVALID,
        )


def create_event(
    db: Session,
    data: EventCreate,
    scope: PointScope,
    household_id: int | None = None,
    user_id: int | None = None,
) -> Event:
    _validate_scope(
        scope,
        household_id,
        user_id,
    )

    if household_id is not None:
        _validate_household(
            db,
            household_id,
        )

    if user_id is not None:
        _validate_user(
            db,
            user_id,
        )

    event = Event(
        **data.model_dump(),
        scope=scope,
        household_id=household_id,
        user_id=user_id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def update_event(
    db: Session,
    event: Event,
    data: EventUpdate,
) -> Event:
    changes = data.model_dump(
        exclude_unset=True,
    )

    for field, value in changes.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


def deactivate_event(
    db: Session,
    event: Event,
) -> None:
    event.is_active = False
    db.commit()


def reactivate_event(
    db: Session,
    event: Event,
) -> Event:
    event.is_active = True
    db.commit()
    db.refresh(event)

    return event