from datetime import date

from sqlalchemy import and_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking_model import Booking
from exceptions import BookingError, TimeNotFound
from logger import logger

from .base_repo import BaseRepository


class BookingRepository(BaseRepository):
    model = Booking

    @classmethod
    async def find_all_booking(cls, user_id: int, date: date, session: AsyncSession):
        try:
            query = (
                select(cls.model)
                .where(
                    and_(
                        cls.model.user_id == user_id, cls.model.date_for_booking >= date
                    )
                )
                .order_by(cls.model.date_for_booking)
            )
            res = await session.execute(query)
            return res.scalars().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Не удалось найти все записи."
            else:
                msg = "Unknown Exc: Не удалось найти все записи."
            logger.error(msg)
            return None

    @classmethod
    async def get_booking(cls, user_id: int, session: AsyncSession, date: date):
        try:
            query = select(cls.model).where(
                and_(cls.model.user_id == user_id, cls.model.date_for_booking == date)
            )

            res = await session.execute(query)
            return res.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Не удалось получить запись."
            else:
                msg = "Unknown Exc: Не удалось получить запись."
            logger.error(msg)
            return None

    @classmethod
    async def select_times(
        cls, user_id: int, session: AsyncSession, booking_id: int, time: tuple[str]
    ):
        try:
            query = select(cls.model).where(
                and_(cls.model.user_id == user_id, cls.model.id == booking_id)
            )
            result = await session.execute(query)
            booking = result.scalar_one_or_none()

            booking.times.remove(time[0])
            booking.selected_times.append((time))
            new_booking = (
                update(cls.model)
                .where(cls.model.id == booking_id)
                .values(times=booking.times, selected_times=booking.selected_times)
            )
            await session.execute(new_booking)
            await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Не удалось сделать запись."
            else:
                msg = "Unknown Exc: Не удалось сделать запись."
            logger.error(msg)
            raise BookingError

    @classmethod
    async def cancel_times(
        cls, user_id: int, session: AsyncSession, booking_id: int, time: str
    ):
        try:
            query = select(cls.model).where(
                and_(cls.model.user_id == user_id, cls.model.id == booking_id)
            )

            result = await session.execute(query)
            booking = result.scalar_one_or_none()

            item_to_remove = None
            for item in booking.selected_times:
                if item[0] == time:
                    item_to_remove = item
                    break

            if item_to_remove:
                booking.selected_times.remove(item_to_remove)
            else:
                raise TimeNotFound

            booking.times.append(item_to_remove[0])
            new_booking = (
                update(cls.model)
                .where(cls.model.id == booking_id)
                .values(times=booking.times, selected_times=booking.selected_times)
            )
            await session.execute(new_booking)
            await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Не удалось получить запись."
            else:
                msg = "Unknown Exc: Не удалось получить запись."
            logger.error(msg)
            return None
