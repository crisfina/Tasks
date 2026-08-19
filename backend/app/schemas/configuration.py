from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)


ConfigurationKey = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*$",
    ),
]

ConfigurationValue = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

ConfigurationDescription = Annotated[
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

class ConfigurationBase(BaseModel):
    key: ConfigurationKey
    value: ConfigurationValue
    description: ConfigurationDescription | None = None

class ConfigurationCreate(ConfigurationBase):
    is_editable: bool = True

class ConfigurationRead(ConfigurationBase):
    id: PositiveId
    is_editable: bool

    model_config = ConfigDict(from_attributes=True)

class ConfigurationUpdate(BaseModel):
    value: ConfigurationValue



