from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base
from app.enums.event_type import EventType

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped [EventType | None] = mapped_column(Enum(EventType), nullable=True)
    default_points: Mapped[int] = mapped_column(Integer, nullable=False)
   