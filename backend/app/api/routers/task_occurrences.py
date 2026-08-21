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
from app.models.task import Task
from app.models.task_occurrence import TaskOccurrence
from app.models.user import User
from app.schemas.task_occurrence import (
    TaskOccurrenceComplete,
    TaskOccurrenceCreate,
    TaskOccurrenceRead,
    TaskOccurrenceUpdate,
)
from app.services.household_service import (
    require_household_manager,
)
from app.services.task_occurrence_service import (
    complete_task_occurrence,
    create_task_occurrence,
    get_task_occurrence_or_raise,
    get_task_occurrences,
    update_task_occurrence,
)
from app.services.task_service import (
    get_task_for_user_or_raise,
)


router = APIRouter(
    tags=["task occurrences"],
)


def _require_task_management(
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

    require_household_manager(
        db,
        task.household_id,
        user_id,
    )


@router.get(
    "/tasks/{task_id}/occurrences",
    response_model=list[TaskOccurrenceRead],
)
def list_task_occurrences(
    task_id: Annotated[
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
    include_completed: Annotated[
        bool,
        Query(),
    ] = False,
) -> list[TaskOccurrence]:
    get_task_for_user_or_raise(
        db,
        task_id,
        current_user.id,
    )

    return get_task_occurrences(
        db,
        task_id,
        include_completed=include_completed,
    )


@router.post(
    "/tasks/{task_id}/occurrences",
    response_model=TaskOccurrenceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_occurrence(
    task_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: TaskOccurrenceCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> TaskOccurrence:
    task = get_task_for_user_or_raise(
        db,
        task_id,
        current_user.id,
    )

    _require_task_management(
        db,
        task,
        current_user.id,
    )

    return create_task_occurrence(
        db,
        task,
        data,
    )


@router.get(
    "/task-occurrences/{occurrence_id}",
    response_model=TaskOccurrenceRead,
)
def get_occurrence(
    occurrence_id: Annotated[
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
) -> TaskOccurrence:
    occurrence = get_task_occurrence_or_raise(
        db,
        occurrence_id,
    )

    get_task_for_user_or_raise(
        db,
        occurrence.task_id,
        current_user.id,
    )

    return occurrence


@router.patch(
    "/task-occurrences/{occurrence_id}",
    response_model=TaskOccurrenceRead,
)
def update_existing_occurrence(
    occurrence_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: TaskOccurrenceUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> TaskOccurrence:
    occurrence = get_task_occurrence_or_raise(
        db,
        occurrence_id,
    )

    task = get_task_for_user_or_raise(
        db,
        occurrence.task_id,
        current_user.id,
    )

    _require_task_management(
        db,
        task,
        current_user.id,
    )

    return update_task_occurrence(
        db,
        occurrence,
        data,
    )


@router.post(
    "/task-occurrences/{occurrence_id}/complete",
    response_model=TaskOccurrenceRead,
)
def complete_occurrence(
    occurrence_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: TaskOccurrenceComplete,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> TaskOccurrence:
    occurrence = get_task_occurrence_or_raise(
        db,
        occurrence_id,
    )

    get_task_for_user_or_raise(
        db,
        occurrence.task_id,
        current_user.id,
    )

    return complete_task_occurrence(
        db,
        occurrence,
        current_user.id,
        data,
    )