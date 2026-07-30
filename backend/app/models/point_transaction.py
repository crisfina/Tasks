from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.event import Event
    from app.models.task_occurrence import TaskOccurrence


from app.db.base import Base


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    points: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    task_occurrence_id: Mapped[int | None] = mapped_column(ForeignKey("task_occurrences.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="point_transactions")
    event: Mapped["Event"] = relationship(back_populates="point_transactions")
    task_occurrence: Mapped["TaskOccurrence"] = relationship(back_populates="point_transactions")