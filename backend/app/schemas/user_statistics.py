from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
)


PositiveId = Annotated[
    int,
    Field(gt=0),
]

NonNegativeInteger = Annotated[
    int,
    Field(ge=0),
]


class UserStatisticsRead(BaseModel):
    id: PositiveId
    user_id: PositiveId
    total_earned_points: NonNegativeInteger
    total_spent_points: NonNegativeInteger
    total_completed_tasks: NonNegativeInteger
    total_minutes_worked: NonNegativeInteger
    minutes_deviation: int
    total_failed_tasks: NonNegativeInteger
    current_streak: NonNegativeInteger
    best_streak: NonNegativeInteger
    updated_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)