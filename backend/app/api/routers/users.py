from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_admin,
    get_current_user,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserDelete,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
    UserUpdateAdmin,
)
from app.services.user_service import (
    change_password,
    deactivate_user,
    get_user_or_raise,
    get_users,
    reactivate_user,
    update_user,
    update_user_admin,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "",
    response_model=list[UserRead],
)
def list_users(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
    include_inactive: bool = False,
) -> list[User]:
    return get_users(
        db,
        include_inactive=include_inactive,
    )


@router.patch(
    "/me",
    response_model=UserRead,
)
def update_my_user(
    data: UserUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    return update_user(
        db,
        current_user,
        data,
    )


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_my_password(
    data: UserPasswordUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Response:
    change_password(
        db,
        current_user,
        data,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_user(
    data: UserDelete,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Response:
    deactivate_user(
        db,
        current_user,
        data.password,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: Annotated[
        int,
        Path(gt=0),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
) -> User:
    return get_user_or_raise(
        db,
        user_id,
        include_inactive=True,
    )


@router.patch(
    "/{user_id}",
    response_model=UserRead,
)
def update_user_as_admin(
    user_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: UserUpdateAdmin,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
) -> User:
    user = get_user_or_raise(
        db,
        user_id,
        include_inactive=True,
    )

    return update_user_admin(
        db,
        user,
        data,
    )


@router.post(
    "/{user_id}/reactivate",
    response_model=UserRead,
)
def reactivate_user_as_admin(
    user_id: Annotated[
        int,
        Path(gt=0),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
) -> User:
    user = get_user_or_raise(
        db,
        user_id,
        include_inactive=True,
    )

    return reactivate_user(
        db,
        user,
    )