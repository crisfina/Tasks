from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import (
    AssignmentModeEnum,
    DifficultyEnum,
    PriorityEnum,
    RepeatTypeEnum,
    UrgencyEnum,
    VisibilityEnum,
)


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
    difficulty: Mapped[DifficultyEnum]
    priority: Mapped[PriorityEnum]
    urgency: Mapped[UrgencyEnum]

    repeat_type: Mapped[RepeatTypeEnum]
    repeat_interval: Mapped[int | None] = mapped_column(nullable=True)

    days_before_due: Mapped[int | None] = mapped_column(nullable=True)
    days_until_due: Mapped[int | None] = mapped_column(nullable=True)

    visibility: Mapped[VisibilityEnum]

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    assignment_mode: Mapped[AssignmentModeEnum | None]

    display_order: Mapped[int | None] = mapped_column(nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )