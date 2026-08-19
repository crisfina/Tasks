from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.point_scope import PointScope

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.household import Household
    from app.models.task_occurrence import TaskOccurrence
    from app.models.user import User


class PointTransaction(Base):
    __tablename__ = "point_transactions"
    __table_args__ = (
        CheckConstraint(
            "(event_id IS NOT NULL AND task_occurrence_id IS NULL) OR "
            "(event_id IS NULL AND task_occurrence_id IS NOT NULL)",
            name="ck_point_transaction_single_source",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    household_id: Mapped[int | None] = mapped_column(
        ForeignKey("households.id"),
    )

    scope: Mapped[PointScope] = mapped_column(
        Enum(PointScope, name="point_scope"),
    )

    points: Mapped[int] = mapped_column(
        Integer,
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id"),
    )

    task_occurrence_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_occurrences.id"),
    )

    user: Mapped["User"] = relationship(
        back_populates="point_transactions",
    )

    event: Mapped["Event | None"] = relationship(
        back_populates="point_transactions",
    )

    task_occurrence: Mapped["TaskOccurrence | None"] = relationship(
        back_populates="point_transactions",
    )

    household: Mapped["Household | None"] = relationship(
        back_populates="point_transactions",
    )

    