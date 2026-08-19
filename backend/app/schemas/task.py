from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)
from pydantic_core import PydanticCustomError

from app.enums import (
    AssignmentMode,
    Difficulty,
    Priority,
    RepeatType,
    Urgency,
    Visibility,
)


TaskTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]

TaskDescription = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=2000,
    ),
]

PositiveId = Annotated[
    int,
    Field(gt=0),
]

PositiveInteger = Annotated[
    int,
    Field(gt=0),
]

NonNegativeInteger = Annotated[
    int,
    Field(ge=0),
]


class TaskBase(BaseModel):
    title: TaskTitle
    description: TaskDescription | None = None
    category_id: PositiveId | None = None
    room_id: PositiveId | None = None
    estimated_minutes: PositiveInteger | None = None
    difficulty: Difficulty
    priority: Priority
    urgency: Urgency
    repeat_type: RepeatType
    repeat_interval: PositiveInteger | None = None
    days_before_due: NonNegativeInteger | None = None
    days_until_due: NonNegativeInteger | None = None
    visibility: Visibility
    household_id: PositiveId | None = None
    assignment_mode: AssignmentMode | None = None
    display_order: NonNegativeInteger | None = None


class TaskCreate(TaskBase):
    assigned_user_ids: list[PositiveId] = Field(
        default_factory=list,
    )

    @field_validator("assigned_user_ids")
    @classmethod
    def validate_assigned_user_ids(
        cls,
        user_ids: list[int],
    ) -> list[int]:
        if len(user_ids) != len(set(user_ids)):
            raise PydanticCustomError(
                "assigned_users_duplicate",
                "Assigned users cannot contain duplicates",
            )

        return user_ids