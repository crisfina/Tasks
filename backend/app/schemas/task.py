from pydantic import BaseModel, ConfigDict, Field

from app.enums import (
    AssignmentMode,
    Difficulty,
    Priority,
    RepeatType,
    Urgency,
    Visibility,
)


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    category_id: int | None = None
    room_id: int | None = None
    estimated_minutes: int | None = None
    difficulty: Difficulty
    priority: Priority
    urgency: Urgency
    repeat_type: RepeatType
    repeat_interval: int | None = None
    days_before_due: int | None = None
    days_until_due: int | None = None
    visibility: Visibility
    household_id: int | None = None
    assignment_mode: AssignmentMode | None = None
    display_order: int | None = None

class TaskCreate(TaskBase):
    assigned_user_ids: list[int] = Field(default_factory=list)

