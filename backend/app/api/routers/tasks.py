from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.services.task_service import (
    create_task,
    deactivate_task,
    get_task_for_user_or_raise,
    get_tasks,
    reactivate_task,
    update_task,
)


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get(
    "",
    response_model=list[TaskRead],
)
def list_tasks(
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
    include_hidden: bool = False,
) -> list[Task]:
    return get_tasks(
        db,
        actor_id=current_user.id,
        household_id=household_id,
        include_hidden=include_hidden,
    )


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_task(
    data: TaskCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Task:
    return create_task(
        db,
        data,
        current_user.id,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
)
def get_task(
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
) -> Task:
    return get_task_for_user_or_raise(
        db,
        task_id,
        current_user.id,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
)
def update_existing_task(
    task_id: Annotated[
        int,
        Path(gt=0),
    ],
    data: TaskUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> Task:
    task = get_task_for_user_or_raise(
        db,
        task_id,
        current_user.id,
    )

    return update_task(
        db,
        task,
        current_user.id,
        data,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
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
) -> Response:
    task = get_task_for_user_or_raise(
        db,
        task_id,
        current_user.id,
    )

    deactivate_task(
        db,
        task,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{task_id}/restore",
    response_model=TaskRead,
)
def restore_deleted_task(
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
) -> Task:
    task = get_task_for_user_or_raise(
        db,
        task_id,
        current_user.id,
        include_inactive=True,
    )

    return reactivate_task(
        db,
        task,
        current_user.id,
    )