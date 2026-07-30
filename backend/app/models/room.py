from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.task import Task


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="room"
    )