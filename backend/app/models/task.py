from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import (
    AssignmentMode,
    Difficulty,
    Priority,
    RepeatType,
    Urgency,
    Visibility,
)

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.room import Room
    from app.models.task_assignment_user import TaskAssignmentUser
    from app.models.task_occurrence import TaskOccurrence
    from app.models.user import User
    from app.models.household import Household


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(200))

    description: Mapped[str | None] = mapped_column(Text)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    estimated_minutes: Mapped[int | None] = mapped_column()

    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty, name="difficulty"))

    priority: Mapped[Priority] = mapped_column(Enum(Priority, name="priority"))

    urgency: Mapped[Urgency] = mapped_column(Enum(Urgency, name="urgency"))

    repeat_type: Mapped[RepeatType] = mapped_column(Enum(RepeatType, name="repeat_type"))

    repeat_interval: Mapped[int | None] = mapped_column()

    days_before_due: Mapped[int | None] = mapped_column()

    days_until_due: Mapped[int | None] = mapped_column()

    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility, name="visibility"))

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    household_id: Mapped[int | None] = mapped_column(ForeignKey("households.id"))

    assignment_mode: Mapped[AssignmentMode | None] = mapped_column(Enum(AssignmentMode, name="assignment_mode"))

    display_order: Mapped[int | None] = mapped_column()

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    category: Mapped["Category"] = relationship(
        back_populates="tasks"
    )

    room: Mapped["Room"] = relationship(
        back_populates="tasks"
    )

    creator: Mapped["User"] = relationship(
        back_populates="created_tasks"
    )

    assigned_users: Mapped[list["TaskAssignmentUser"]] = relationship(
        back_populates="task"
    )

    occurrences: Mapped[list["TaskOccurrence"]] = relationship(
        back_populates="task"
    )

    household: Mapped["Household | None"] = relationship(
        back_populates="tasks",
    )