from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

from app.enums.event_type import EventType
from app.enums.point_scope import PointScope


EventName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

EventDescription = Annotated[
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

PositivePoints = Annotated[
    int,
    Field(gt=0),
]


class EventBase(BaseModel):
    name: EventName
    description: EventDescription | None = None
    event_type: EventType
    default_points: PositivePoints


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: PositiveId
    scope: PointScope
    household_id: PositiveId | None
    user_id: PositiveId | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class EventUpdate(BaseModel):
    name: EventName | None = None
    description: EventDescription | None = None
    event_type: EventType | None = None
    default_points: PositivePoints | None = None