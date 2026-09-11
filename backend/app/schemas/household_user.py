from datetime import datetime
from typing import Annotated

from pydantic import (
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
)

from app.enums.household_role import HouseholdRole


PositiveId = Annotated[
    int,
    Field(gt=0),
]


class HouseholdUserCreate(BaseModel):
    user_id: PositiveId
    role: HouseholdRole = HouseholdRole.MEMBER


class HouseholdUserRead(BaseModel):
    household_id: PositiveId
    user_id: PositiveId
    username: str = Field(
        validation_alias=AliasPath("user", "username"),
    )
    color: str = Field(
        validation_alias=AliasPath("user", "color"),
    )
    role: HouseholdRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HouseholdUserUpdate(BaseModel):
    role: HouseholdRole