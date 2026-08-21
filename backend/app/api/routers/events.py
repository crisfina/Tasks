from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    AuthorizationError,
    ErrorCode,
)
from app.db.database import get_db
from app.enums.point_scope import PointScope
from app.models.event import Event
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventRead,
    EventUpdate,
)
from app.services.event_service import (
    create_event,
    deactivate_event,
    get_event_or_raise,
    get_events,
    reactivate_event,
    update_event,
)
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
    require_household_owner,
)


router = APIRouter(
    prefix="/events",
    tags=["events"],
)


def _require_event_access(
    db: Session,
    event: Event,
    user_id: int,
) -> None:
    if event.scope == PointScope.PERSONAL:
        if event.user_id != user_id:
            raise AuthorizationError(
                ErrorCode.EVENT_USER_INVALID,
            )

        return

    if event.household_id is None:
        raise AuthorizationError(
            ErrorCode.EVENT_HOUSEHOLD_INVALID,
        )

    get_household_or_raise(
        db,
        event.household_id,
    )

    get_membership_or_raise(
        db,
        event.household_id,
        user_id,
    )


def _require_event_management(
    db: Session,
    event: Event,
    user_id: int,
) -> None:
    if event.scope == PointScope.PERSONAL:
        if event.user_id != user_id:
            raise AuthorizationError(
                ErrorCode.EVENT_USER_INVALID,
            )

        return

    if event.household_id is None:
        raise AuthorizationError(
            ErrorCode.EVENT_HOUSEHOLD_INVALID,
        )

    require_household_owner(
        db,
        event.household_id,
        user_id,
    )


@router.get(
    "",
    response_model=list[EventRead],
)
def list_events(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    household_id: Annotated[
        int | None,
        Query(gt=0),
    ] = None,
    include_inactive: bool = False,
) -> list[Event]:
    if household_id is None:
        return get_events(
            db,
            scope=PointScope.PERSONAL,
            user_id=current_user.id,
            include_inactive=include_inactive,
        )

    get_household_or_raise(
        db,
        household_id,
    )

    get_membership_or_raise(
        db,
        household_id,
        current_user.id,
    )

    return get_events(
        db,
        scope=PointScope.HOUSEHOLD,
        household_id=household_id,
        include_inactive=include_inactive,
    )


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_event(
    data: EventCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    household_id: Annotated[
        int | None,
        Query(gt=0),
    ] = None,
) -> Event:
    if household_id is None:
        return create_event(
            db,
            data,
            scope=PointScope.PERSONAL,
            user_id=current_user.id,
        )

    require_household_owner(
        db,
        household_id,
        current_user.id,
    )

    return create_event(
        db,
        data,
        scope=PointScope.HOUSEHOLD,
        household_id=household_id,
    )


@router.get(
    "/{event_id}",
    response_model=EventRead,
)
def get_event(
    event_id: Annotated[
        int,
        Path(gt=0),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Event:
    event = get_event_or_raise(
        db,
        event_id,
    )

    _require_event_access(
        db,
        event,
        current_user.id,
    )

    return event


@router.patch(
    "/{event_id}",
    response_model=EventRead,
)
def update_existing_event(
    event_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: EventUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Event:
    event = get_event_or_raise(
        db,
        event_id,
    )

    _require_event_management(
        db,
        event,
        current_user.id,
    )

    return update_event(
        db,
        event,
        data,
    )


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: Annotated[
        int,
        Path(gt=0),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Response:
    event = get_event_or_raise(
        db,
        event_id,
    )

    _require_event_management(
        db,
        event,
        current_user.id,
    )

    deactivate_event(
        db,
        event,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{event_id}/restore",
    response_model=EventRead,
)
def restore_deleted_event(
    event_id: Annotated[
        int,
        Path(gt=0),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Event:
    event = get_event_or_raise(
        db,
        event_id,
        include_inactive=True,
    )

    _require_event_management(
        db,
        event,
        current_user.id,
    )

    return reactivate_event(
        db,
        event,
    )