from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

CategoryName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

IconPath = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

Color = Annotated[
    str,
    StringConstraints(
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
]

PositiveId = Annotated[
    int,
    Field(gt=0),
]

NonNegativeInteger = Annotated[
    int,
    Field(ge=0),
]

class CategoryBase(BaseModel):
    name: CategoryName
    icon: IconPath = "/images/default-category.svg"
    color: Color = "#FFFFFF"
    display_order: NonNegativeInteger | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: PositiveId
    household_id: PositiveId
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class CategoryUpdate(BaseModel):
    name: CategoryName | None = None
    icon: IconPath | None = None
    color: Color | None = None
    display_order: NonNegativeInteger | None = None