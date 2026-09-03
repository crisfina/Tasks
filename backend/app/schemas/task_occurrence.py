from typing import Annotated, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)
from pydantic_core import PydanticCustomError


PositiveInteger = Annotated[
    int,
    Field(gt=0),
]

PositiveId = Annotated[
    int,
    Field(gt=0),
]

NonNegativeInteger = Annotated[
    int,
    Field(ge=0),
]

OccurrenceNotes = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=2000,
    ),
]


class TaskOccurrenceBase(BaseModel):
    assigned_user_id: PositiveId | None = None
    available_from: AwareDatetime
    due_date: AwareDatetime
    notes: OccurrenceNotes | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.due_date < self.available_from:
            raise PydanticCustomError(
                "occurrence_dates_invalid",
                "Due date cannot be earlier than available date",
            )

        return self


class TaskOccurrenceCreate(TaskOccurrenceBase):
    pass


class TaskOccurrenceRead(TaskOccurrenceBase):
    id: PositiveId
    task_id: PositiveId
    completed_at: AwareDatetime | None
    completed_by_user_id: PositiveId | None
    failed_at: AwareDatetime | None
    failed_by_user_id: PositiveId | None
    realized_minutes: PositiveInteger | None
    awarded_points: NonNegativeInteger | None
    created_at: AwareDatetime
    updated_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class TaskOccurrenceUpdate(BaseModel):
    assigned_user_id: PositiveId | None = None
    available_from: AwareDatetime | None = None
    due_date: AwareDatetime | None = None
    notes: OccurrenceNotes | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if (
            self.available_from is not None
            and self.due_date is not None
            and self.due_date < self.available_from
        ):
            raise PydanticCustomError(
                "occurrence_dates_invalid",
                "Due date cannot be earlier than available date",
            )

        return self


class TaskOccurrenceComplete(BaseModel):
    realized_minutes: PositiveInteger
    notes: OccurrenceNotes | None = None


class TaskOccurrenceFail(BaseModel):
    penalize: bool = False
    penalized_user_ids: list[PositiveId] = Field(
        default_factory=list,
    )

    @model_validator(mode="after")
    def validate_penalized_user_ids(self) -> Self:
        if len(self.penalized_user_ids) != len(
            set(self.penalized_user_ids),
        ):
            raise PydanticCustomError(
                "penalized_users_duplicate",
                "penalized_users_duplicate",
            )

        return self