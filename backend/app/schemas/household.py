from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)


HouseholdName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

PositiveId = Annotated[
    int,
    Field(gt=0),
]


class HouseholdBase(BaseModel):
    name: HouseholdName


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdRead(HouseholdBase):
    id: PositiveId
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HouseholdUpdate(BaseModel):
    name: HouseholdName | None = None