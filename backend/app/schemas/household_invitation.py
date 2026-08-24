from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.enums.household_role import HouseholdRole


PositiveId = Annotated[
    int,
    Field(gt=0),
]

InvitationCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=64,
    ),
]


class HouseholdInvitationCreate(BaseModel):
    role: HouseholdRole = HouseholdRole.MEMBER


class HouseholdInvitationAccept(BaseModel):
    code: InvitationCode


class HouseholdInvitationRead(BaseModel):
    id: PositiveId
    household_id: PositiveId
    created_by_user_id: PositiveId
    accepted_by_user_id: PositiveId | None
    role: HouseholdRole
    expires_at: datetime
    accepted_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HouseholdInvitationCreated(HouseholdInvitationRead):
    code: str