from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)

from app.enums.user_role import UserRole


Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=50,
        pattern=r"^[\w.-]+$",
    ),
]

Email = Annotated[
    EmailStr,
    StringConstraints(
        max_length=255,
    ),
]

Password = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
    ),
]

Color = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    ),
]

AvatarUrl = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

PositiveId = Annotated[
    int,
    Field(gt=0),
]


class UserBase(BaseModel):
    username: Username
    email: Email
    color: Color | None = None
    avatar_url: AvatarUrl | None = None


class UserCreate(UserBase):
    password: Password


class UserRead(UserBase):
    id: PositiveId
    is_active: bool
    role: UserRole
    created_at: AwareDatetime
    updated_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Username | None = None
    email: Email | None = None
    color: Color | None = None
    avatar_url: AvatarUrl | None = None


class UserUpdateAdmin(BaseModel):
    username: Username | None = None
    email: Email | None = None
    color: Color | None = None
    avatar_url: AvatarUrl | None = None
    is_active: bool | None = None
    role: UserRole | None = None


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: Password


class UserDelete(BaseModel):
    password: str