from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.event_type import EventType
from app.enums.point_scope import PointScope

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.point_transaction import PointTransaction
    from app.models.user import User


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type"),
    )

    scope: Mapped[PointScope] = mapped_column(
        Enum(PointScope, name="point_scope"),
    )

    household_id: Mapped[int | None] = mapped_column(
        ForeignKey("households.id"),
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
    )

    default_points: Mapped[int] = mapped_column(
        Integer,
    )

    household: Mapped["Household | None"] = relationship(
        back_populates="events",
    )

    user: Mapped["User | None"] = relationship(
        back_populates="events",
    )

    point_transactions: Mapped[list["PointTransaction"]] = relationship(
        back_populates="event",
    )