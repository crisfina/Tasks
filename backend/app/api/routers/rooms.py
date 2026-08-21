from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.room import Room
from app.models.user import User
from app.schemas.room import (
    RoomCreate,
    RoomRead,
    RoomUpdate,
)
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
)
from app.services.room_service import (
    create_room,
    deactivate_room,
    get_household_rooms,
    get_room_or_raise,
    restore_room,
    update_room,
)


router = APIRouter(
    prefix="/households/{household_id}/rooms",
    tags=["rooms"],
)


@router.get(
    "",
    response_model=list[RoomRead],
)
def list_rooms(
    household_id: Annotated[
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
) -> list[Room]:
    return get_household_rooms(
        db,
        household_id,
        current_user.id,
    )


@router.post(
    "",
    response_model=RoomRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_room(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: RoomCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Room:
    return create_room(
        db,
        household_id,
        current_user.id,
        data,
    )


@router.get(
    "/{room_id}",
    response_model=RoomRead,
)
def get_room(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    room_id: Annotated[
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
) -> Room:
    get_household_or_raise(
        db,
        household_id,
    )

    get_membership_or_raise(
        db,
        household_id,
        current_user.id,
    )

    return get_room_or_raise(
        db,
        household_id,
        room_id,
    )


@router.patch(
    "/{room_id}",
    response_model=RoomRead,
)
def update_existing_room(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    room_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: RoomUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Room:
    return update_room(
        db,
        household_id,
        room_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_room(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    room_id: Annotated[
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
    deactivate_room(
        db,
        household_id,
        room_id,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{room_id}/restore",
    response_model=RoomRead,
)
def restore_deleted_room(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    room_id: Annotated[
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
) -> Room:
    return restore_room(
        db,
        household_id,
        room_id,
        current_user.id,
    )