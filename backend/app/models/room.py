from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.task import Task


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint(
            "household_id",
            "name",
            name="uq_room_household_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id"),
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    color: Mapped[str] = mapped_column(
        String(7),
        default="#FFFFFF",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    display_order: Mapped[int | None] = mapped_column(
        Integer,
    )

    household: Mapped["Household"] = relationship(
        back_populates="rooms",
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="room",
    )