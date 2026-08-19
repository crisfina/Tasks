from typing import Annotated

from pydantic import (
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


class TaskAssignmentUserCreate(BaseModel):
    user_id: PositiveId
    order: NonNegativeInteger | None = None


class TaskAssignmentUserRead(BaseModel):
    id: PositiveId
    task_id: PositiveId
    user_id: PositiveId
    order: NonNegativeInteger | None

    model_config = ConfigDict(from_attributes=True)

class TaskAssignmentUserUpdate(BaseModel):
    order: NonNegativeInteger | None