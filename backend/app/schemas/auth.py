from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
)


LoginIdentifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=255,
    ),
]

PasswordInput = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=128,
    ),
]

PositiveInteger = Annotated[
    int,
    Field(gt=0),
]


class LoginRequest(BaseModel):
    identifier: LoginIdentifier
    password: PasswordInput


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: PositiveInteger