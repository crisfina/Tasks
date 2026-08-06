from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.household_role import HouseholdRole

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.user import User
    from aap.models.event import Event


class HouseholdUser(Base):
    __tablename__ = "household_users"

    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )

    role: Mapped[HouseholdRole] = mapped_column(
        Enum(HouseholdRole, name="household_role"),
        default=HouseholdRole.MEMBER,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    household: Mapped["Household"] = relationship(
        back_populates="members",
    )

    user: Mapped["User"] = relationship(
        back_populates="household_memberships",
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="household",
    )