from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Date, JSON
from datetime import date
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user_model import User
    from .time_model import Times


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True)
    date_for_booking: Mapped[date] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    times: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    selected_times: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=[])

    user: Mapped['User'] = relationship('User', back_populates='bookings')
    list_times: Mapped[list['Times']] = relationship('Times', back_populates='booking')


