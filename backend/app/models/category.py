from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.task import Task


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    icon: Mapped[str] = mapped_column(String(255), default="/images/default-category.svg")
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(nullable=True)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="category"
    )