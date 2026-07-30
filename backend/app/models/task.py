from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import (
    AssignmentModeEnum,
    DifficultyEnum,
    PriorityEnum,
    RepeatTypeEnum,
    UrgencyEnum,
    VisibilityEnum,
)

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.room import Room
    from app.models.task_assignment_user import TaskAssignmentUser
    from app.models.task_occurrence import TaskOccurrence
    from app.models.user import User


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
        nullable=False
    )

    estimated_minutes: Mapped[int | None] = mapped_column(nullable=True)

    difficulty: Mapped[DifficultyEnum] = mapped_column(
        Enum(DifficultyEnum),
        nullable=False
    )

    priority: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum),
        nullable=False
    )

    urgency: Mapped[UrgencyEnum] = mapped_column(
        Enum(UrgencyEnum),
        nullable=False
    )

    repeat_type: Mapped[RepeatTypeEnum] = mapped_column(
        Enum(RepeatTypeEnum),
        nullable=False
    )

    repeat_interval: Mapped[int | None] = mapped_column(nullable=True)

    days_before_due: Mapped[int | None] = mapped_column(nullable=True)
    days_until_due: Mapped[int | None] = mapped_column(nullable=True)

    visibility: Mapped[VisibilityEnum] = mapped_column(
        Enum(VisibilityEnum),
        nullable=False
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    assignment_mode: Mapped[AssignmentModeEnum | None] = mapped_column(
        Enum(AssignmentModeEnum),
        nullable=True
    )

    display_order: Mapped[int | None] = mapped_column(nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
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