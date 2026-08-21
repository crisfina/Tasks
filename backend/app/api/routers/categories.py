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
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from app.services.category_service import (
    create_category,
    deactivate_category,
    get_category_or_raise,
    get_household_categories,
    restore_category,
    update_category,
)
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
)


router = APIRouter(
    prefix="/households/{household_id}/categories",
    tags=["categories"],
)


@router.get(
    "",
    response_model=list[CategoryRead],
)
def list_categories(
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
) -> list[Category]:
    return get_household_categories(
        db,
        household_id,
        current_user.id,
    )


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_category(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: CategoryCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Category:
    return create_category(
        db,
        household_id,
        current_user.id,
        data,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
)
def get_category(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    category_id: Annotated[
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
) -> Category:
    get_household_or_raise(
        db,
        household_id,
    )

    get_membership_or_raise(
        db,
        household_id,
        current_user.id,
    )

    return get_category_or_raise(
        db,
        household_id,
        category_id,
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
)
def update_existing_category(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    category_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: CategoryUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Category:
    return update_category(
        db,
        household_id,
        category_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    category_id: Annotated[
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
    deactivate_category(
        db,
        household_id,
        category_id,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{category_id}/restore",
    response_model=CategoryRead,
)
def restore_deleted_category(
    household_id: Annotated[
        int,
        Path(gt=0),
    ],
    category_id: Annotated[
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
) -> Category:
    return restore_category(
        db,
        household_id,
        category_id,
        current_user.id,
    )