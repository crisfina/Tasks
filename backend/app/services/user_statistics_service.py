from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_statistics import UserStatistics


def get_user_statistics(
    db: Session,
    user_id: int,
) -> UserStatistics | None:
    statement = select(UserStatistics).where(
        UserStatistics.user_id == user_id,
    )

    return db.scalar(statement)


def get_or_create_user_statistics(
    db: Session,
    user: User,
) -> UserStatistics:
    statistics = get_user_statistics(
        db,
        user.id,
    )

    if statistics is not None:
        return statistics

    statistics = UserStatistics(
        user_id=user.id,
    )

    db.add(statistics)
    db.commit()
    db.refresh(statistics)

    return statistics