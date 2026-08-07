from pydantic import BaseModel, ConfigDict

from app.enums.user_role import UserRole


class UserBase(BaseModel):
    username: str
    email: str
    color: str | None = None
    avatar_url: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    color: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


class UserUpdateAdmin(BaseModel):
    username: str | None = None
    email: str | None = None
    color: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None
    
class UserDelete(BaseModel):
    password: str