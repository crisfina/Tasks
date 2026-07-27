from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.task import Task


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(nullable=True)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="room"
    )