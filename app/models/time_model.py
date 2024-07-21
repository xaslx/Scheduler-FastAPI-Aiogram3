from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user_model import User
    from .booking_model import Booking


class Times(Base):
    __tablename__ = 'times'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    booking_id: Mapped[int] = mapped_column(ForeignKey('bookings.id'))
    time: Mapped[str]

    user: Mapped['User'] = relationship('User', back_populates='times')
    booking: Mapped['Booking'] = relationship('Booking', back_populates='list_times')
