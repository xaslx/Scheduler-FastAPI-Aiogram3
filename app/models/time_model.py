from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, ForeignKey
from datetime import date, time, datetime
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .user_model import User
    from .booking_model import Booking


class Times(Base):
    __tablename__ = 'times'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    booking_id: Mapped[int] = mapped_column(ForeignKey('bookings.id'))
    time: Mapped[str]
    booking: Mapped['Booking'] = relationship(back_populates='times')
    user: Mapped['User'] = relationship(back_populates='times')