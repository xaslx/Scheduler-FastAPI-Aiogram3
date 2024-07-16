from .base_repo import BaseRepository
from app.models.booking_model import Booking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Time, insert, and_, select, update
from datetime import date
from exceptions import TimeNotFound

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
        return res.scalars().first()

    
    @classmethod
    async def find_all_booking(cls, user_id: int, date: date, session: AsyncSession):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.date_for_booking >= date
            )
        ).order_by(cls.model.date_for_booking)
        res = await session.execute(query)
        return res.scalars().all()


    @classmethod
    async def get_booking(cls, user_id: int, session: AsyncSession, date: date):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.date_for_booking == date
            )
        )

        res = await session.execute(query)
        return res.scalars().first()

    @classmethod
    async def select_times(cls, user_id: int, session: AsyncSession, booking_id: int, time: str):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.id == booking_id
            )
        )
        result = await session.execute(query)
        booking = result.scalar_one_or_none()
        if time not in booking.times:
            raise TimeNotFound
        booking.times.remove(time)
        booking.selected_times.append(time)
        new_booking = update(cls.model).where(cls.model.id == booking_id).values(times=booking.times, selected_times=booking.selected_times)
        await session.execute(new_booking)
        await session.commit()

    @classmethod
    async def cancel_times(cls, user_id: int, session: AsyncSession, booking_id: int, time: str):
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.id == booking_id
            )
        )
        result = await session.execute(query)
        booking = result.scalar_one_or_none()

        if time not in booking.selected_times:
            raise TimeNotFound

        booking.times.append(time)
        booking.selected_times.remove(time)

        new_booking = update(cls.model).where(cls.model.id == booking_id).values(times=booking.times, selected_times=booking.selected_times)
        await session.execute(new_booking)
        await session.commit()


        