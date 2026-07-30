from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.event import Event
    from app.models.task_occurrence import TaskOccurrence


from app.db.base import Base


class PointTransaction(Base):
    __tablename__ = "point_transactions"
    __table_args__ = (
        CheckConstraint(
            "(event_id IS NOT NULL AND task_occurrence_id IS NULL) OR "
            "(event_id IS NULL AND task_occurrence_id IS NOT NULL)",
            name="ck_point_transaction_single_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"))
    task_occurrence_id: Mapped[int | None] = mapped_column(ForeignKey("task_occurrences.id"))

    user: Mapped["User"] = relationship(back_populates="point_transactions")
    event: Mapped["Event"] = relationship(back_populates="point_transactions")
    task_occurrence: Mapped["TaskOccurrence"] = relationship(back_populates="point_transactions")