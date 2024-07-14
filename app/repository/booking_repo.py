from .base_repo import BaseRepository
from app.models.booking_model import Booking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, and_, select, update
from datetime import date


class BookingRepository(BaseRepository):
    model = Booking


    @classmethod
    async def find_booking(cls, user_id: int, date: date, session: AsyncSession):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.date_for_booking == date
            )
        )
        res = await session.execute(query)
        return res.mappings().one_or_none()

    @classmethod
    async def get_booking(cls, user_id: int, session: AsyncSession, date: date):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.date_for_booking == date
            )
        )

        res = await session.execute(query)
        return res.mappings().one_or_none()

    @classmethod
    async def update_times(cls, user_id: int, session: AsyncSession, booking_id: int):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.id == booking_id
            )
        )
        result = await session.execute(query)
        booking = result.scalar_one_or_none()
        booking.times.remove('16:00')
        new_booking = update(cls.model).where(cls.model.id == booking_id).values(times=booking.times)
        await session.execute(new_booking)
        await session.commit()

        