from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    ErrorCode,
    NotFoundError,
)
from app.enums import (
    AssignmentMode,
    Visibility,
)
from app.enums.household_role import HouseholdRole
from app.models.category import Category
from app.models.household import Household
from app.models.household_user import HouseholdUser
from app.models.room import Room
from app.models.task import Task
from app.models.task_assignment_user import TaskAssignmentUser
from app.models.task_occurrence import TaskOccurrence
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


DEFAULT_DAYS_UNTIL_DUE = 2


def get_task_by_id(
    db: Session,
    task_id: int,
    include_inactive: bool = False,
) -> Task | None:
    statement = select(Task).where(
        Task.id == task_id,
    )

    if not include_inactive:
        statement = statement.where(
            Task.is_active.is_(True),
        )

    return db.scalar(statement)


def get_task_or_raise(
    db: Session,
    task_id: int,
    include_inactive: bool = False,
) -> Task:
    task = get_task_by_id(
        db,
        task_id,
        include_inactive=include_inactive,
    )

    if task is None:
        raise NotFoundError(
            ErrorCode.TASK_NOT_FOUND,
        )

    return task


def _get_household_membership(
    db: Session,
    household_id: int,
    user_id: int,
) -> HouseholdUser | None:
    statement = (
        select(HouseholdUser)
        .join(
            Household,
            Household.id == HouseholdUser.household_id,
        )
        .where(
            HouseholdUser.household_id == household_id,
            HouseholdUser.user_id == user_id,
            Household.is_active.is_(True),
        )
    )

    return db.scalar(statement)


def _require_task_access(
    db: Session,
    task: Task,
    user_id: int,
) -> None:
    if task.household_id is None:
        if task.created_by != user_id:
            raise AuthorizationError(
                ErrorCode.TASK_ACCESS_DENIED,
            )

        return

    membership = _get_household_membership(
        db,
        task.household_id,
        user_id,
    )

    if membership is None:
        raise AuthorizationError(
            ErrorCode.TASK_ACCESS_DENIED,
        )


def _require_task_edit_permission(
    db: Session,
    task: Task,
    user_id: int,
) -> None:
    if task.household_id is None:
        if task.created_by != user_id:
            raise AuthorizationError(
                ErrorCode.TASK_ACCESS_DENIED,
            )

        return

    membership = _get_household_membership(
        db,
        task.household_id,
        user_id,
    )

    if (
        membership is None
        or membership.role not in (
            HouseholdRole.OWNER,
            HouseholdRole.MANAGER,
        )
    ):
        raise AuthorizationError(
            ErrorCode.HOUSEHOLD_MANAGER_REQUIRED,
        )


def get_task_for_user_or_raise(
    db: Session,
    task_id: int,
    user_id: int,
    include_inactive: bool = False,
) -> Task:
    task = get_task_or_raise(
        db,
        task_id,
        include_inactive=include_inactive,
    )

    _require_task_access(
        db,
        task,
        user_id,
    )

    return task


def get_tasks(
    db: Session,
    actor_id: int,
    household_id: int | None = None,
    include_inactive: bool = False,
    include_hidden: bool = False,
) -> list[Task]:
    statement = select(Task)

    if household_id is None:
        statement = statement.where(
            Task.household_id.is_(None),
            Task.created_by == actor_id,
        )
    else:
        household_statement = select(Household.id).where(
            Household.id == household_id,
            Household.is_active.is_(True),
        )

        if db.scalar(household_statement) is None:
            raise NotFoundError(
                ErrorCode.HOUSEHOLD_NOT_FOUND,
            )

        membership = _get_household_membership(
            db,
            household_id,
            actor_id,
        )

        if membership is None:
            raise AuthorizationError(
                ErrorCode.TASK_ACCESS_DENIED,
            )

        statement = statement.where(
            Task.household_id == household_id,
            Task.visibility != Visibility.PRIVATE,
        )

    if not include_inactive:
        statement = statement.where(
            Task.is_active.is_(True),
        )

    if not include_hidden:
        statement = statement.where(
            Task.visibility != Visibility.HIDDEN,
        )

    statement = statement.order_by(
        Task.display_order.asc().nulls_last(),
        Task.id,
    )

    return list(
        db.scalars(statement).all(),
    )


def _validate_household(
    db: Session,
    household_id: int,
    user_id: int,
) -> None:
    household_statement = select(Household.id).where(
        Household.id == household_id,
        Household.is_active.is_(True),
    )

    if db.scalar(household_statement) is None:
        raise NotFoundError(
            ErrorCode.HOUSEHOLD_NOT_FOUND,
        )

    membership = _get_household_membership(
        db,
        household_id,
        user_id,
    )

    if (
        membership is None
        or membership.role not in (
            HouseholdRole.OWNER,
            HouseholdRole.MANAGER,
        )
    ):
        raise AuthorizationError(
            ErrorCode.HOUSEHOLD_MANAGER_REQUIRED,
        )


def _validate_visibility(
    visibility: Visibility,
    household_id: int | None,
) -> None:
    if (
        visibility == Visibility.SHARED
        and household_id is None
    ):
        raise BusinessRuleError(
            ErrorCode.TASK_HOUSEHOLD_REQUIRED,
        )

    if (
        visibility == Visibility.PRIVATE
        and household_id is not None
    ):
        raise BusinessRuleError(
            ErrorCode.TASK_VISIBILITY_INVALID,
        )


def _validate_category(
    db: Session,
    category_id: int | None,
    household_id: int | None,
) -> None:
    if category_id is None:
        return

    if household_id is None:
        raise BusinessRuleError(
            ErrorCode.TASK_HOUSEHOLD_REQUIRED,
        )

    statement = select(Category.id).where(
        Category.id == category_id,
        Category.household_id == household_id,
        Category.is_active.is_(True),
    )

    if db.scalar(statement) is None:
        raise BusinessRuleError(
            ErrorCode.TASK_CATEGORY_INVALID,
        )


def _validate_room(
    db: Session,
    room_id: int | None,
    household_id: int | None,
) -> None:
    if room_id is None:
        return

    if household_id is None:
        raise BusinessRuleError(
            ErrorCode.TASK_HOUSEHOLD_REQUIRED,
        )

    statement = select(Room.id).where(
        Room.id == room_id,
        Room.household_id == household_id,
        Room.is_active.is_(True),
    )

    if db.scalar(statement) is None:
        raise BusinessRuleError(
            ErrorCode.TASK_ROOM_INVALID,
        )


def _validate_assigned_users(
    db: Session,
    user_ids: list[int],
    household_id: int | None,
) -> None:
    if not user_ids:
        return

    if household_id is None:
        raise BusinessRuleError(
            ErrorCode.TASK_HOUSEHOLD_REQUIRED,
        )

    statement = (
        select(HouseholdUser.user_id)
        .join(
            User,
            User.id == HouseholdUser.user_id,
        )
        .where(
            HouseholdUser.household_id == household_id,
            HouseholdUser.user_id.in_(user_ids),
            User.is_active.is_(True),
        )
    )

    valid_user_ids = set(
        db.scalars(statement).all(),
    )

    if valid_user_ids != set(user_ids):
        raise BusinessRuleError(
            ErrorCode.TASK_ASSIGNED_USER_INVALID,
        )


def _validate_assignment_mode(
    assignment_mode: AssignmentMode | None,
    assigned_user_ids: list[int],
) -> None:
    has_assigned_users = bool(
        assigned_user_ids,
    )

    if (
        assignment_mode in (
            None,
            AssignmentMode.NONE,
        )
        and has_assigned_users
    ):
        raise BusinessRuleError(
            ErrorCode.TASK_ASSIGNMENT_MODE_INVALID,
        )

    if (
        assignment_mode not in (
            None,
            AssignmentMode.NONE,
        )
        and not has_assigned_users
    ):
        raise BusinessRuleError(
            ErrorCode.TASK_ASSIGNMENT_MODE_INVALID,
        )


def _validate_repeat_configuration(
    repeat_type: object | None,
    repeat_interval: int | None,
) -> None:
    if repeat_type is None and repeat_interval is not None:
        raise BusinessRuleError(
            ErrorCode.TASK_REPEAT_INTERVAL_INVALID,
        )


def _replace_assigned_users(
    db: Session,
    task: Task,
    user_ids: list[int],
) -> None:
    statement = delete(TaskAssignmentUser).where(
        TaskAssignmentUser.task_id == task.id,
    )

    db.execute(statement)

    for order, user_id in enumerate(
        user_ids,
    ):
        assignment = TaskAssignmentUser(
            task_id=task.id,
            user_id=user_id,
            order=order,
        )
        db.add(assignment)


def _create_first_occurrence(
    db: Session,
    task: Task,
    assigned_user_ids: list[int],
) -> None:
    now = datetime.now(UTC)

    days_until_due = (
        task.days_until_due
        if task.days_until_due is not None
        else DEFAULT_DAYS_UNTIL_DUE
    )

    assigned_user_id = (
        assigned_user_ids[0]
        if len(assigned_user_ids) == 1
        else None
    )

    occurrence = TaskOccurrence(
        task_id=task.id,
        assigned_user_id=assigned_user_id,
        available_from=now,
        due_date=now + timedelta(
            days=days_until_due,
        ),
    )

    db.add(occurrence)


def create_task(
    db: Session,
    data: TaskCreate,
    created_by: int,
) -> Task:
    task_data = data.model_dump(
        exclude={"assigned_user_ids"},
    )
    assigned_user_ids = data.assigned_user_ids

    household_id = task_data.get("household_id")
    category_id = task_data.get("category_id")
    room_id = task_data.get("room_id")
    visibility = task_data["visibility"]
    assignment_mode = task_data.get("assignment_mode")
    repeat_type = task_data.get("repeat_type")
    repeat_interval = task_data.get("repeat_interval")

    if household_id is not None:
        _validate_household(
            db,
            household_id,
            created_by,
        )

    _validate_visibility(
        visibility,
        household_id,
    )
    _validate_category(
        db,
        category_id,
        household_id,
    )
    _validate_room(
        db,
        room_id,
        household_id,
    )
    _validate_assigned_users(
        db,
        assigned_user_ids,
        household_id,
    )
    _validate_assignment_mode(
        assignment_mode,
        assigned_user_ids,
    )
    _validate_repeat_configuration(
        repeat_type,
        repeat_interval,
    )

    if repeat_type is not None and repeat_interval is None:
        task_data["repeat_interval"] = 1

    task = Task(
        **task_data,
        created_by=created_by,
    )

    db.add(task)
    db.flush()

    _replace_assigned_users(
        db,
        task,
        assigned_user_ids,
    )
    _create_first_occurrence(
        db,
        task,
        assigned_user_ids,
    )

    db.commit()
    db.refresh(task)

    return task


def update_task(
    db: Session,
    task: Task,
    actor_id: int,
    data: TaskUpdate,
) -> Task:
    _require_task_edit_permission(
        db,
        task,
        actor_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
    )

    assigned_user_ids = changes.pop(
        "assigned_user_ids",
        None,
    )

    category_id = changes.get(
        "category_id",
        task.category_id,
    )
    room_id = changes.get(
        "room_id",
        task.room_id,
    )
    visibility = changes.get(
        "visibility",
        task.visibility,
    )
    assignment_mode = changes.get(
        "assignment_mode",
        task.assignment_mode,
    )
    repeat_type = changes.get(
        "repeat_type",
        task.repeat_type,
    )
    repeat_interval = changes.get(
        "repeat_interval",
        task.repeat_interval,
    )

    current_assigned_user_ids = [
        assignment.user_id
        for assignment in task.assigned_users
    ]

    effective_assigned_user_ids = (
        assigned_user_ids
        if assigned_user_ids is not None
        else current_assigned_user_ids
    )

    _validate_visibility(
        visibility,
        task.household_id,
    )
    _validate_category(
        db,
        category_id,
        task.household_id,
    )
    _validate_room(
        db,
        room_id,
        task.household_id,
    )
    _validate_assigned_users(
        db,
        effective_assigned_user_ids,
        task.household_id,
    )
    _validate_assignment_mode(
        assignment_mode,
        effective_assigned_user_ids,
    )

    if (
        "repeat_type" in changes
        and repeat_type is None
    ):
        changes["repeat_interval"] = None
        repeat_interval = None

    _validate_repeat_configuration(
        repeat_type,
        repeat_interval,
    )

    if repeat_type is not None and repeat_interval is None:
        changes["repeat_interval"] = 1

    for field, value in changes.items():
        setattr(task, field, value)

    if assigned_user_ids is not None:
        _replace_assigned_users(
            db,
            task,
            assigned_user_ids,
        )

    db.commit()
    db.refresh(task)

    return task


def deactivate_task(
    db: Session,
    task: Task,
    actor_id: int,
) -> None:
    _require_task_edit_permission(
        db,
        task,
        actor_id,
    )

    task.is_active = False
    db.commit()


def reactivate_task(
    db: Session,
    task: Task,
    actor_id: int,
) -> Task:
    _require_task_edit_permission(
        db,
        task,
        actor_id,
    )

    task.is_active = True

    db.commit()
    db.refresh(task)

    return task