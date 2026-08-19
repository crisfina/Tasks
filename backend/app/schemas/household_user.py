from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

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
    role: HouseholdRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HouseholdUserUpdate(BaseModel):
    role: HouseholdRole