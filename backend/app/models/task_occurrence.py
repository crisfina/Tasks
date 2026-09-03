from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.point_transaction import PointTransaction
    from app.models.task import Task
    from app.models.user import User


class TaskOccurrence(Base):
    __tablename__ = "task_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id")
    )

    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id")
    )

    available_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    completed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id")
    )

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    failed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id")
    )

    realized_minutes: Mapped[int | None] = mapped_column(
        Integer
    )

    awarded_points: Mapped[int | None] = mapped_column(
        Integer
    )

    notes: Mapped[str | None] = mapped_column(
        Text
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

    task: Mapped["Task"] = relationship(
        back_populates="occurrences"
    )

    assigned_user: Mapped["User | None"] = relationship(
        foreign_keys=[assigned_user_id],
        back_populates="assigned_task_occurrences",
    )

    completed_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[completed_by_user_id],
        back_populates="completed_task_occurrences",
    )

    failed_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[failed_by_user_id],
        back_populates="failed_task_occurrences",
    )

    point_transactions: Mapped[list["PointTransaction"]] = relationship(
        back_populates="task_occurrence"
    )