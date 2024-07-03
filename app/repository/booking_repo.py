from .base_repo import BaseRepository
from app.models.booking_model import Booking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, and_, select
from datetime import date


class BookingRepository(BaseRepository):
    model = Booking


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
