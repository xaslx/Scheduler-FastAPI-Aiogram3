from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Time
from datetime import datetime, time
from typing import TYPE_CHECKING
from app.utils.generate_time import moscow_tz
from .booking_model import Booking
from app.utils.current_time import current_time


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    surname: Mapped[str] = mapped_column(String(255))
    profile_photo: Mapped[str] = mapped_column(String(255), default='default.jpg')
    role: Mapped[str] = mapped_column(String(255), default='user')
    email: Mapped[str] = mapped_column(String(255), unique=True)
    personal_link: Mapped[str] = mapped_column(String(255), unique=True)
    telegram_link: Mapped[str] = mapped_column(String(255), default=None, nullable=True)
    hashed_password: Mapped[str]
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=current_time())
    is_active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[str | None] = mapped_column(String(500), default=None, nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    start_time: Mapped[time] = mapped_column(Time, default=time(7, 0))
    end_time: Mapped[time] = mapped_column(Time, default=time(20, 0))
    interval: Mapped[int] = mapped_column(default=30)
    

    bookings: Mapped[list['Booking']] = relationship('Booking', back_populates='user')
