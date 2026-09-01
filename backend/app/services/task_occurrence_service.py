from calendar import monthrange
from datetime import UTC, datetime, timedelta
from random import choice

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusinessRuleError,
    ErrorCode,
    NotFoundError,
)
from app.enums import AssignmentMode, RepeatType
from app.models.household_user import HouseholdUser
from app.models.task import Task
from app.models.task_occurrence import TaskOccurrence
from app.models.user import User
from app.schemas.task_occurrence import (
    TaskOccurrenceComplete,
    TaskOccurrenceCreate,
    TaskOccurrenceUpdate,
)
from app.services.point_transaction_service import (
    create_task_occurrence_transaction,
)


def get_task_occurrence_by_id(
    db: Session,
    occurrence_id: int,
) -> TaskOccurrence | None:
    statement = select(TaskOccurrence).where(
        TaskOccurrence.id == occurrence_id,
    )

    return db.scalar(statement)


def get_task_occurrence_or_raise(
    db: Session,
    occurrence_id: int,
) -> TaskOccurrence:
    occurrence = get_task_occurrence_by_id(
        db,
        occurrence_id,
    )

    if occurrence is None:
        raise NotFoundError(
            ErrorCode.TASK_OCCURRENCE_NOT_FOUND,
        )

    return occurrence


def get_task_occurrences(
    db: Session,
    task_id: int,
    include_completed: bool = False,
) -> list[TaskOccurrence]:
    statement = select(TaskOccurrence).where(
        TaskOccurrence.task_id == task_id,
    )

    if not include_completed:
        statement = statement.where(
            TaskOccurrence.completed_at.is_(None),
        )

    statement = statement.order_by(
        TaskOccurrence.available_from,
        TaskOccurrence.id,
    )

    return list(
        db.scalars(statement).all(),
    )


def _validate_assigned_user(
    db: Session,
    task: Task,
    user_id: int | None,
) -> None:
    if user_id is None:
        return

    user_statement = select(User.id).where(
        User.id == user_id,
        User.is_active.is_(True),
    )

    if db.scalar(user_statement) is None:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_USER_INVALID,
        )

    if task.household_id is None:
        if user_id != task.created_by:
            raise BusinessRuleError(
                ErrorCode.TASK_OCCURRENCE_USER_INVALID,
            )

        return

    membership_statement = select(
        HouseholdUser.user_id,
    ).where(
        HouseholdUser.household_id == task.household_id,
        HouseholdUser.user_id == user_id,
    )

    if db.scalar(membership_statement) is None:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_USER_INVALID,
        )


def create_task_occurrence(
    db: Session,
    task: Task,
    data: TaskOccurrenceCreate,
) -> TaskOccurrence:
    if not task.is_active:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_TASK_INACTIVE,
        )

    _validate_assigned_user(
        db,
        task,
        data.assigned_user_id,
    )

    occurrence = TaskOccurrence(
        task_id=task.id,
        **data.model_dump(),
    )

    db.add(occurrence)
    db.commit()
    db.refresh(occurrence)

    return occurrence


def update_task_occurrence(
    db: Session,
    occurrence: TaskOccurrence,
    data: TaskOccurrenceUpdate,
) -> TaskOccurrence:
    if occurrence.completed_at is not None:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_ALREADY_COMPLETED,
        )

    changes = data.model_dump(
        exclude_unset=True,
    )

    available_from = changes.get(
        "available_from",
        occurrence.available_from,
    )

    due_date = changes.get(
        "due_date",
        occurrence.due_date,
    )

    if due_date < available_from:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_DATES_INVALID,
        )

    if "assigned_user_id" in changes:
        _validate_assigned_user(
            db,
            occurrence.task,
            changes["assigned_user_id"],
        )

    for field, value in changes.items():
        setattr(occurrence, field, value)

    db.commit()
    db.refresh(occurrence)

    return occurrence


def _add_months(
    value: datetime,
    months: int,
) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1

    day = min(
        value.day,
        monthrange(year, month)[1],
    )

    return value.replace(
        year=year,
        month=month,
        day=day,
    )


def _calculate_next_available_from(
    completed_at: datetime,
    repeat_type: RepeatType,
    repeat_interval: int,
) -> datetime:
    if repeat_type == RepeatType.DAILY:
        return completed_at + timedelta(
            days=repeat_interval,
        )

    if repeat_type == RepeatType.WEEKLY:
        return completed_at + timedelta(
            weeks=repeat_interval,
        )

    if repeat_type == RepeatType.BIWEEKLY:
        return completed_at + timedelta(
            weeks=2 * repeat_interval,
        )

    if repeat_type == RepeatType.MONTHLY:
        return _add_months(
            completed_at,
            repeat_interval,
        )

    if repeat_type in (
        RepeatType.SEMESTERLY,
        RepeatType.TWICE_A_YEAR,
    ):
        return _add_months(
            completed_at,
            6 * repeat_interval,
        )

    if repeat_type == RepeatType.YEARLY:
        return _add_months(
            completed_at,
            12 * repeat_interval,
        )

    raise BusinessRuleError(
        ErrorCode.TASK_REPEAT_INTERVAL_INVALID,
    )


def _get_next_assigned_user_id(
    task: Task,
    current_user_id: int | None,
) -> int | None:
    assignments = sorted(
        task.assigned_users,
        key=lambda assignment: (
            assignment.order is None,
            assignment.order,
            assignment.id,
        ),
    )

    user_ids = [
        assignment.user_id
        for assignment in assignments
    ]

    if not user_ids:
        return None

    if task.assignment_mode in (
        None,
        AssignmentMode.NONE,
    ):
        return None

    if task.assignment_mode in (
        AssignmentMode.MANUAL,
        AssignmentMode.FIXED,
    ):
        if current_user_id in user_ids:
            return current_user_id

        return user_ids[0]

    if task.assignment_mode == AssignmentMode.ALTERNATING:
        if current_user_id not in user_ids:
            return user_ids[0]

        current_index = user_ids.index(
            current_user_id,
        )

        next_index = (
            current_index + 1
        ) % len(user_ids)

        return user_ids[next_index]

    if task.assignment_mode == AssignmentMode.RANDOM:
        return choice(user_ids)

    return user_ids[0]


def _create_next_occurrence(
    db: Session,
    task: Task,
    completed_at: datetime,
    current_user_id: int | None,
) -> None:
    if (
        not task.is_active
        or task.repeat_type is None
    ):
        return

    repeat_interval = task.repeat_interval or 1

    due_date = _calculate_next_available_from(
        completed_at,
        task.repeat_type,
        repeat_interval,
    )

    available_from = (
        due_date - timedelta(days=task.days_before_due)
        if task.days_before_due is not None
        else completed_at
    )

    next_occurrence = TaskOccurrence(
        task_id=task.id,
        assigned_user_id=_get_next_assigned_user_id(
            task,
            current_user_id,
        ),
        available_from=available_from,
        due_date=due_date,
    )

    db.add(next_occurrence)


def complete_task_occurrence(
    db: Session,
    occurrence: TaskOccurrence,
    completed_by_user_id: int,
    data: TaskOccurrenceComplete,
) -> TaskOccurrence:
    if occurrence.completed_at is not None:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_ALREADY_COMPLETED,
        )

    now = datetime.now(UTC)

    if now < occurrence.available_from:
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_NOT_AVAILABLE,
        )

    _validate_assigned_user(
        db,
        occurrence.task,
        completed_by_user_id,
    )

    if (
        occurrence.assigned_user_id is not None
        and occurrence.assigned_user_id
        != completed_by_user_id
    ):
        raise BusinessRuleError(
            ErrorCode.TASK_OCCURRENCE_USER_INVALID,
        )

    occurrence.completed_at = now
    occurrence.completed_by_user_id = completed_by_user_id
    occurrence.realized_minutes = data.realized_minutes

    if data.notes is not None:
        occurrence.notes = data.notes

    _create_next_occurrence(
        db,
        occurrence.task,
        now,
        occurrence.assigned_user_id,
    )

    try:
        if occurrence.task.awards_points:
            create_task_occurrence_transaction(
                db,
                occurrence,
            )
        else:
            occurrence.awarded_points = None
            db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(occurrence)

    return occurrence