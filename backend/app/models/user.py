from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.user_role import UserRole


if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.event import Event
    from app.models.household_user import HouseholdUser
    from app.models.point_transaction import PointTransaction
    from app.models.task import Task
    from app.models.task_assignment_user import TaskAssignmentUser
    from app.models.task_occurrence import TaskOccurrence
    from app.models.user_statistics import UserStatistics


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
    )

    color: Mapped[str] = mapped_column(
        String(7),
        default="#FFFFFF",
    )

    avatar_url: Mapped[str] = mapped_column(
        String(255),
        default="/images/default-avatar.png",
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.USER,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    created_tasks: Mapped[list["Task"]] = relationship(
        back_populates="creator",
    )

    assigned_tasks: Mapped[list["TaskAssignmentUser"]] = relationship(
        back_populates="user",
    )

    assigned_task_occurrences: Mapped[list["TaskOccurrence"]] = relationship(
        foreign_keys="TaskOccurrence.assigned_user_id",
        back_populates="assigned_user",
    )

    completed_task_occurrences: Mapped[list["TaskOccurrence"]] = relationship(
        foreign_keys="TaskOccurrence.completed_by_user_id",
        back_populates="completed_by_user",
    )

    statistics: Mapped["UserStatistics"] = relationship(
        back_populates="user",
    )

    point_transactions: Mapped[list["PointTransaction"]] = relationship(
        back_populates="user",
    )

    household_memberships: Mapped[list["HouseholdUser"]] = relationship(
        back_populates="user",
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="user",
    )

    categories: Mapped[list["Category"]] = relationship(
        back_populates="user",
    )