from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    ErrorCode,
    NotFoundError,
)
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
    require_household_owner,
)


def get_room_by_id(
    db: Session,
    household_id: int,
    room_id: int,
    include_inactive: bool = False,
) -> Room | None:
    statement = select(Room).where(
        Room.id == room_id,
        Room.household_id == household_id,
    )

    if not include_inactive:
        statement = statement.where(
            Room.is_active.is_(True),
        )

    return db.scalar(statement)


def get_room_or_raise(
    db: Session,
    household_id: int,
    room_id: int,
    include_inactive: bool = False,
) -> Room:
    room = get_room_by_id(
        db,
        household_id,
        room_id,
        include_inactive=include_inactive,
    )

    if room is None:
        raise NotFoundError(
            ErrorCode.ROOM_NOT_FOUND,
        )

    return room


def get_household_rooms(
    db: Session,
    household_id: int,
    actor_id: int,
) -> list[Room]:
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
        select(Room)
        .where(
            Room.household_id == household_id,
            Room.is_active.is_(True),
        )
        .order_by(
            Room.display_order.asc().nulls_last(),
            Room.name,
        )
    )

    return list(
        db.scalars(statement).all(),
    )


def _ensure_unique_room_name(
    db: Session,
    household_id: int,
    name: str,
    exclude_room_id: int | None = None,
) -> None:
    statement = select(Room).where(
        Room.household_id == household_id,
        func.lower(Room.name) == name.lower(),
    )

    if exclude_room_id is not None:
        statement = statement.where(
            Room.id != exclude_room_id,
        )

    existing_room = db.scalar(statement)

    if existing_room is not None:
        raise ConflictError(
            ErrorCode.ROOM_NAME_EXISTS,
        )


def create_room(
    db: Session,
    household_id: int,
    actor_id: int,
    data: RoomCreate,
) -> Room:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    _ensure_unique_room_name(
        db,
        household_id,
        data.name,
    )

    room_data = data.model_dump(
        exclude_none=True,
    )

    room = Room(
        household_id=household_id,
        **room_data,
    )

    db.add(room)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(
            ErrorCode.ROOM_NAME_EXISTS,
        ) from error

    db.refresh(room)

    return room


def update_room(
    db: Session,
    household_id: int,
    room_id: int,
    actor_id: int,
    data: RoomUpdate,
) -> Room:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    room = get_room_or_raise(
        db,
        household_id,
        room_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if "name" in changes:
        _ensure_unique_room_name(
            db,
            household_id,
            changes["name"],
            exclude_room_id=room.id,
        )

    for field, value in changes.items():
        setattr(room, field, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(
            ErrorCode.ROOM_NAME_EXISTS,
        ) from error

    db.refresh(room)

    return room


def deactivate_room(
    db: Session,
    household_id: int,
    room_id: int,
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

    room = get_room_or_raise(
        db,
        household_id,
        room_id,
    )

    room.is_active = False
    db.commit()


def restore_room(
    db: Session,
    household_id: int,
    room_id: int,
    actor_id: int,
) -> Room:
    get_household_or_raise(
        db,
        household_id,
    )

    require_household_owner(
        db,
        household_id,
        actor_id,
    )

    room = get_room_or_raise(
        db,
        household_id,
        room_id,
        include_inactive=True,
    )

    room.is_active = True

    db.commit()
    db.refresh(room)

    return room