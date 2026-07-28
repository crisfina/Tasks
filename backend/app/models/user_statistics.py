from db.base import Base
from datetime import datetime, UTC
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class UserStatistics(Base):
    __tablename__ = "user_statistics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    total_earned_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_spent_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_completed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_minutes_worked: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minutes_deviation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_failed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(
        back_populates="statistics"
    )