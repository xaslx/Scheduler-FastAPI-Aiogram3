from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from .user_model import User


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_for_booking: Mapped[date] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    times: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    selected_times: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=[])

    user: Mapped["User"] = relationship("User", back_populates="bookings")
