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
from app.models.household import Household
from app.models.household_user import HouseholdUser
from app.models.user import User
from app.schemas.household import (
    HouseholdCreate,
    HouseholdRead,
    HouseholdUpdate,
)
from app.schemas.household_user import (
    HouseholdUserCreate,
    HouseholdUserRead,
    HouseholdUserUpdate,
)
from app.services.household_service import (
    add_household_member,
    create_household,
    deactivate_household,
    get_household_members,
    get_household_or_raise,
    get_membership_or_raise,
    get_user_households,
    remove_household_member,
    restore_household,
    update_household,
    update_household_member,
)


router = APIRouter(
    prefix="/households",
    tags=["households"],
)


@router.get(
    "",
    response_model=list[HouseholdRead],
)
def list_my_households(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> list[Household]:
    return get_user_households(
        db,
        current_user.id,
    )


@router.post(
    "",
    response_model=HouseholdRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_household(
    data: HouseholdCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Household:
    return create_household(
        db,
        data,
        current_user,
    )


@router.get(
    "/{household_id}",
    response_model=HouseholdRead,
)
def get_household(
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
) -> Household:
    household = get_household_or_raise(
        db,
        household_id,
    )

    get_membership_or_raise(
        db,
        household_id,
        current_user.id,
    )

    return household


@router.patch(
    "/{household_id}",
    response_model=HouseholdRead,
)
def update_existing_household(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: HouseholdUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Household:
    return update_household(
        db,
        household_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{household_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_household(
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
) -> Response:
    deactivate_household(
        db,
        household_id,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{household_id}/restore",
    response_model=HouseholdRead,
)
def restore_deleted_household(
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
) -> Household:
    return restore_household(
        db,
        household_id,
        current_user.id,
    )


@router.get(
    "/{household_id}/members",
    response_model=list[HouseholdUserRead],
)
def list_household_members(
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
) -> list[HouseholdUser]:
    return get_household_members(
        db,
        household_id,
        current_user.id,
    )


@router.post(
    "/{household_id}/members",
    response_model=HouseholdUserRead,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: HouseholdUserCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> HouseholdUser:
    return add_household_member(
        db,
        household_id,
        current_user.id,
        data,
    )


@router.patch(
    "/{household_id}/members/{user_id}",
    response_model=HouseholdUserRead,
)
def update_member(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    user_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: HouseholdUserUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> HouseholdUser:
    return update_household_member(
        db,
        household_id,
        user_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{household_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    user_id: Annotated[
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
    remove_household_member(
        db,
        household_id,
        user_id,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )