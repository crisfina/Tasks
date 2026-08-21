from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusinessRuleError,
    ErrorCode,
    NotFoundError,
)
from app.enums import Difficulty, Urgency
from app.enums.event_type import EventType
from app.enums.point_scope import PointScope
from app.models.event import Event
from app.models.household_user import HouseholdUser
from app.models.point_transaction import PointTransaction
from app.models.task_occurrence import TaskOccurrence
from app.models.user import User
from app.models.user_statistics import UserStatistics


BASE_TASK_POINTS = 2


def get_point_transaction_by_id(
    db: Session,
    transaction_id: int,
) -> PointTransaction | None:
    statement = select(PointTransaction).where(
        PointTransaction.id == transaction_id,
    )

    return db.scalar(statement)


def get_point_transaction_or_raise(
    db: Session,
    transaction_id: int,
) -> PointTransaction:
    transaction = get_point_transaction_by_id(
        db,
        transaction_id,
    )

    if transaction is None:
        raise NotFoundError(
            ErrorCode.POINT_TRANSACTION_NOT_FOUND,
        )

    return transaction


def get_user_transactions(
    db: Session,
    user_id: int,
    scope: PointScope | None = None,
    household_id: int | None = None,
) -> list[PointTransaction]:
    statement = select(PointTransaction).where(
        PointTransaction.user_id == user_id,
    )

    if scope is not None:
        statement = statement.where(
            PointTransaction.scope == scope,
        )

    if household_id is not None:
        statement = statement.where(
            PointTransaction.household_id == household_id,
        )

    statement = statement.order_by(
        PointTransaction.created_at.desc(),
        PointTransaction.id.desc(),
    )

    return list(
        db.scalars(statement).all(),
    )


def get_user_balance(
    db: Session,
    user_id: int,
    scope: PointScope,
    household_id: int | None = None,
) -> int:
    if (
        scope == PointScope.HOUSEHOLD
        and household_id is None
    ):
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_SCOPE_INVALID,
        )

    if (
        scope == PointScope.PERSONAL
        and household_id is not None
    ):
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_SCOPE_INVALID,
        )

    statement = select(
        func.coalesce(
            func.sum(PointTransaction.points),
            0,
        ),
    ).where(
        PointTransaction.user_id == user_id,
        PointTransaction.scope == scope,
    )

    if scope == PointScope.HOUSEHOLD:
        statement = statement.where(
            PointTransaction.household_id == household_id,
        )
    else:
        statement = statement.where(
            PointTransaction.household_id.is_(None),
        )

    return int(
        db.scalar(statement) or 0,
    )


def _validate_user(
    db: Session,
    user_id: int,
) -> None:
    statement = select(User.id).where(
        User.id == user_id,
        User.is_active.is_(True),
    )

    if db.scalar(statement) is None:
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_USER_INVALID,
        )


def _validate_household_member(
    db: Session,
    household_id: int,
    user_id: int,
) -> None:
    statement = select(
        HouseholdUser.user_id,
    ).where(
        HouseholdUser.household_id == household_id,
        HouseholdUser.user_id == user_id,
    )

    if db.scalar(statement) is None:
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_USER_INVALID,
        )


def _get_or_create_statistics(
    db: Session,
    user_id: int,
) -> UserStatistics:
    statement = select(UserStatistics).where(
        UserStatistics.user_id == user_id,
    )

    statistics = db.scalar(statement)

    if statistics is None:
        statistics = UserStatistics(
            user_id=user_id,
        )
        db.add(statistics)
        db.flush()

    return statistics


def _update_point_statistics(
    db: Session,
    user_id: int,
    points: int,
) -> UserStatistics:
    statistics = _get_or_create_statistics(
        db,
        user_id,
    )

    if points > 0:
        statistics.total_earned_points += points
    else:
        statistics.total_spent_points += abs(points)

    return statistics


def _calculate_event_points(
    event: Event,
) -> int:
    if event.event_type in (
        EventType.PENALTY,
        EventType.PURCHASE,
    ):
        return -event.default_points

    return event.default_points


def create_event_transaction(
    db: Session,
    event: Event,
    user_id: int,
    reason: str | None = None,
) -> PointTransaction:
    if not event.is_active:
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_EVENT_INVALID,
        )

    _validate_user(
        db,
        user_id,
    )

    if event.scope == PointScope.HOUSEHOLD:
        if (
            event.household_id is None
            or event.user_id is not None
        ):
            raise BusinessRuleError(
                ErrorCode.POINT_TRANSACTION_SCOPE_INVALID,
            )

        _validate_household_member(
            db,
            event.household_id,
            user_id,
        )

    elif event.scope == PointScope.PERSONAL:
        if (
            event.user_id != user_id
            or event.household_id is not None
        ):
            raise BusinessRuleError(
                ErrorCode.POINT_TRANSACTION_SCOPE_INVALID,
            )

    else:
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_SCOPE_INVALID,
        )

    points = _calculate_event_points(
        event,
    )

    if points < 0:
        current_balance = get_user_balance(
            db,
            user_id,
            event.scope,
            event.household_id,
        )

        if current_balance < abs(points):
            raise BusinessRuleError(
                ErrorCode.INSUFFICIENT_POINTS,
            )

    transaction = PointTransaction(
        user_id=user_id,
        household_id=event.household_id,
        scope=event.scope,
        points=points,
        reason=reason or event.name,
        event_id=event.id,
        task_occurrence_id=None,
    )

    db.add(transaction)

    _update_point_statistics(
        db,
        user_id,
        points,
    )

    db.commit()
    db.refresh(transaction)

    return transaction


def calculate_task_points(
    occurrence: TaskOccurrence,
) -> int:
    task = occurrence.task
    points = BASE_TASK_POINTS

    if task.urgency in (
        Urgency.HIGH,
        Urgency.VERY_HIGH,
    ):
        points *= 2

    if task.difficulty in (
        Difficulty.HARD,
        Difficulty.VERY_HARD,
    ):
        points *= 4

    if (
        occurrence.completed_at is not None
        and occurrence.completed_at <= occurrence.due_date
    ):
        points *= 2

    return points


def create_task_occurrence_transaction(
    db: Session,
    occurrence: TaskOccurrence,
) -> PointTransaction:
    if (
        occurrence.completed_at is None
        or occurrence.completed_by_user_id is None
    ):
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_OCCURRENCE_INVALID,
        )

    existing_statement = select(
        PointTransaction.id,
    ).where(
        PointTransaction.task_occurrence_id == occurrence.id,
    )

    if db.scalar(existing_statement) is not None:
        raise BusinessRuleError(
            ErrorCode.POINT_TRANSACTION_SOURCE_INVALID,
        )

    task = occurrence.task
    user_id = occurrence.completed_by_user_id

    _validate_user(
        db,
        user_id,
    )

    if task.household_id is None:
        scope = PointScope.PERSONAL
        household_id = None
    else:
        scope = PointScope.HOUSEHOLD
        household_id = task.household_id

        _validate_household_member(
            db,
            household_id,
            user_id,
        )

    points = calculate_task_points(
        occurrence,
    )

    occurrence.awarded_points = points

    transaction = PointTransaction(
        user_id=user_id,
        household_id=household_id,
        scope=scope,
        points=points,
        reason=task.title,
        event_id=None,
        task_occurrence_id=occurrence.id,
    )

    db.add(transaction)

    statistics = _update_point_statistics(
        db,
        user_id,
        points,
    )

    statistics.total_completed_tasks += 1
    statistics.total_minutes_worked += (
        occurrence.realized_minutes or 0
    )

    if task.estimated_minutes is not None:
        statistics.minutes_deviation += (
            (occurrence.realized_minutes or 0)
            - task.estimated_minutes
        )

    statistics.current_streak += 1
    statistics.best_streak = max(
        statistics.best_streak,
        statistics.current_streak,
    )

    db.commit()
    db.refresh(transaction)

    return transaction