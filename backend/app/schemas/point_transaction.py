from datetime import datetime
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from app.enums.point_scope import PointScope


PositiveId = Annotated[
    int,
    Field(gt=0),
]

TransactionReason = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]


class PointTransactionRead(BaseModel):
    id: PositiveId
    user_id: PositiveId
    household_id: PositiveId | None
    scope: PointScope
    points: int
    reason: TransactionReason | None
    created_at: datetime
    event_id: PositiveId | None
    task_occurrence_id: PositiveId | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("points")
    @classmethod
    def validate_points(cls, points: int) -> int:
        if points == 0:
            raise PydanticCustomError(
                "points_cannot_be_zero",
                "Points cannot be zero",
            )

        return points

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if (
            self.scope == PointScope.HOUSEHOLD
            and self.household_id is None
        ):
            raise PydanticCustomError(
                "household_required",
                "A household transaction requires a household",
            )

        if (
            self.scope == PointScope.PERSONAL
            and self.household_id is not None
        ):
            raise PydanticCustomError(
                "household_not_allowed",
                "A personal transaction cannot have a household",
            )

        return self

    @model_validator(mode="after")
    def validate_source(self) -> Self:
        has_event = self.event_id is not None
        has_task_occurrence = self.task_occurrence_id is not None

        if has_event == has_task_occurrence:
            raise PydanticCustomError(
                "transaction_source_invalid",
                "A transaction must have exactly one source",
            )

        return self