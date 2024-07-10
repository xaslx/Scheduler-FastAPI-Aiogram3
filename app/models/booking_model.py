from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, ForeignKey, Date, Time, ARRAY, JSON
from datetime import date, time, datetime
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .user_model import User



class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True)
    date_for_booking: Mapped[date] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    times: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    user: Mapped['User'] = relationship(back_populates='bookings')


