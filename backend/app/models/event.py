from sqlalchemy import String, Text, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base
from app.enums.event_type import EventType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.point_transaction import PointTransaction

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    event_type: Mapped [EventType] = mapped_column(Enum(EventType, name="event_type"))
    default_points: Mapped[int] = mapped_column(Integer)

    point_transactions: Mapped[list["PointTransaction"]] = relationship(
        back_populates="event"
    )