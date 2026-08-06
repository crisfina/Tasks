from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.household_user import HouseholdUser
    from app.models.point_transaction import PointTransaction
    from app.models.task import Task
    from app.models.room import Room
    from app.models.category import Category


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
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

    members: Mapped[list["HouseholdUser"]] = relationship(
        back_populates="household",
    )

    point_transactions: Mapped[list["PointTransaction"]] = relationship(
        back_populates="household",
    )

    tasks: Mapped[list["Task"]] = relationship(
    back_populates="household",
    )

    rooms: Mapped[list["Room"]] = relationship(
        back_populates="household",
    )

    categories: Mapped[list["Category"]] = relationship(
        back_populates="household",
    )