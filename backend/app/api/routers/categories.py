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
    create_household_category,
    create_personal_category,
    deactivate_household_category,
    deactivate_personal_category,
    get_household_categories,
    get_household_category_or_raise,
    get_personal_categories,
    get_personal_category_or_raise,
    restore_household_category,
    restore_personal_category,
    update_household_category,
    update_personal_category,
)
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
)


router = APIRouter(
    tags=["categories"],
)


@router.get(
    "/categories",
    response_model=list[CategoryRead],
)
def list_personal_categories(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> list[Category]:
    return get_personal_categories(
        db,
        current_user.id,
    )


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_personal_category(
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
    return create_personal_category(
        db,
        current_user.id,
        data,
    )


@router.get(
    "/categories/{category_id}",
    response_model=CategoryRead,
)
def get_personal_category(
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
    return get_personal_category_or_raise(
        db,
        current_user.id,
        category_id,
    )


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryRead,
)
def update_existing_personal_category(
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
    return update_personal_category(
        db,
        current_user.id,
        category_id,
        data,
    )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_personal_category(
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
    deactivate_personal_category(
        db,
        current_user.id,
        category_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/categories/{category_id}/restore",
    response_model=CategoryRead,
)
def restore_deleted_personal_category(
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
    return restore_personal_category(
        db,
        current_user.id,
        category_id,
    )


@router.get(
    "/households/{household_id}/categories",
    response_model=list[CategoryRead],
)
def list_household_categories(
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
    "/households/{household_id}/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_household_category(
    household_id: Annotated[int, Path(gt=0)],
    data: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    return create_household_category(
        db,
        household_id,
        current_user.id,
        data,
    )


@router.get(
    "/households/{household_id}/categories/{category_id}",
    response_model=CategoryRead,
)
def get_household_category(
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

    return get_household_category_or_raise(
        db,
        household_id,
        category_id,
    )


@router.patch(
    "/households/{household_id}/categories/{category_id}",
    response_model=CategoryRead,
)
def update_existing_household_category(
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
    return update_household_category(
        db,
        household_id,
        category_id,
        current_user.id,
        data,
    )


@router.delete(
    "/households/{household_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_household_category(
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
    deactivate_household_category(
        db,
        household_id,
        category_id,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/households/{household_id}/categories/{category_id}/restore",
    response_model=CategoryRead,
)
def restore_deleted_household_category(
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
    return restore_household_category(
        db,
        household_id,
        category_id,
        current_user.id,
    )