from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
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
from app.models.point_transaction import PointTransaction
from app.models.user import User
from app.schemas.point_transaction import (
    PointTransactionRead,
)
from app.services.event_service import get_event_or_raise
from app.services.household_service import (
    get_household_or_raise,
    get_membership_or_raise,
)
from app.services.point_transaction_service import (
    create_event_transaction,
    get_point_transaction_or_raise,
    get_user_balance,
    get_user_transactions,
)


router = APIRouter(
    prefix="/point-transactions",
    tags=["point transactions"],
)


@router.get(
    "",
    response_model=list[PointTransactionRead],
)
def list_my_transactions(
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
) -> list[PointTransaction]:
    if household_id is None:
        return get_user_transactions(
            db,
            current_user.id,
            scope=PointScope.PERSONAL,
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

    return get_user_transactions(
        db,
        current_user.id,
        scope=PointScope.HOUSEHOLD,
        household_id=household_id,
    )


@router.get(
    "/balance",
    response_model=int,
)
def get_my_balance(
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
) -> int:
    if household_id is None:
        return get_user_balance(
            db,
            current_user.id,
            PointScope.PERSONAL,
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

    return get_user_balance(
        db,
        current_user.id,
        PointScope.HOUSEHOLD,
        household_id,
    )


@router.post(
    "/events/{event_id}",
    response_model=PointTransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction_from_event(
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
) -> PointTransaction:
    event = get_event_or_raise(
        db,
        event_id,
    )

    if event.scope == PointScope.PERSONAL:
        if event.user_id != current_user.id:
            raise AuthorizationError(
                ErrorCode.POINT_TRANSACTION_EVENT_INVALID,
            )
    else:
        if event.household_id is None:
            raise AuthorizationError(
                ErrorCode.POINT_TRANSACTION_EVENT_INVALID,
            )

        get_household_or_raise(
            db,
            event.household_id,
        )

        get_membership_or_raise(
            db,
            event.household_id,
            current_user.id,
        )

    return create_event_transaction(
        db,
        event,
        current_user.id,
    )


@router.get(
    "/{transaction_id}",
    response_model=PointTransactionRead,
)
def get_transaction(
    transaction_id: Annotated[
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
) -> PointTransaction:
    transaction = get_point_transaction_or_raise(
        db,
        transaction_id,
    )

    if transaction.user_id != current_user.id:
        raise AuthorizationError(
            ErrorCode.POINT_TRANSACTION_USER_INVALID,
        )

    return transaction