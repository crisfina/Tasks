
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user_statistics import UserStatistics

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.task_assignment_user import TaskAssignmentUser
    from app.models.task_occurrence import TaskOccurrence


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255))

    color: Mapped[str] = mapped_column(
        String(7),
        default="#FFFFFF"
    )

    avatar_url: Mapped[str] = mapped_column(
        String(255),
        default="/images/default-avatar.png"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    created_tasks: Mapped[list["Task"]] = relationship(
        back_populates="creator"
    )

    assigned_tasks: Mapped[list["TaskAssignmentUser"]] = relationship(
    back_populates="user"
    )

    task_occurrences: Mapped[list["TaskOccurrence"]] = relationship(
    back_populates="user"
    )

    statistics: Mapped["UserStatistics"] = relationship(
    back_populates="user"
    )