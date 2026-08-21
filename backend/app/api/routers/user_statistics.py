from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.user_statistics import UserStatistics
from app.schemas.user_statistics import UserStatisticsRead
from app.services.user_statistics_service import (
    get_or_create_user_statistics,
)


router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
)


@router.get(
    "/me",
    response_model=UserStatisticsRead,
)
def get_my_statistics(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> UserStatistics:
    return get_or_create_user_statistics(
        db,
        current_user,
    )