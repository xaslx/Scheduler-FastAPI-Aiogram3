from datetime import date

from sqlalchemy import and_, insert, select

from app.models.booking_model import Booking
from app.models.telegram_model import Telegram
from app.models.user_model import User
from app.repository.booking_repo import BookingRepository
from app.repository.user_repo import UserRepository
from app.schemas.tg_schema import TelegramOut
from app.schemas.user_schema import UserOut
from database import async_session_maker


class BotService:
    model = Telegram

    @classmethod
    async def add_new_user(cls, telegram_id: int) -> None:
        async with async_session_maker() as session:
            query = insert(cls.model).values(telegram_id=telegram_id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def find_all_users(cls) -> list[TelegramOut]:
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_user_by_tg_id(cls, telegram_id: int) -> TelegramOut:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(telegram_id=telegram_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_user(cls, **filter_by) -> UserOut:
        async with async_session_maker() as session:
            user: User = await UserRepository.find_one_or_none(
                session=session, **filter_by
            )
            if user:
                user_out: UserOut = UserOut.model_validate(user)
                return user_out
            return None

    @classmethod
    async def get_all_bookings(cls, user_id: int, date: date):
        async with async_session_maker() as session:
            return await BookingRepository.find_all_booking(
                user_id=user_id, session=session, date=date
            )

    @classmethod
    async def get_booking(cls, user_id: int, date: date):
        async with async_session_maker() as session:
            return await BookingRepository.get_booking(
                user_id=user_id, date=date, session=session
            )

    @classmethod
    async def add_booking(cls, **data):
        async with async_session_maker() as session:
            return await BookingRepository.add(session=session, **data)

    @classmethod
    async def cancel_booking(cls, user_id: int, booking_id: int, time: str):
        async with async_session_maker() as session:
            return await BookingRepository.cancel_times(
                user_id=user_id, session=session, time=time, booking_id=booking_id
            )

    @classmethod
    async def new_booking(cls, user_id: int, booking_id: int, time: str):
        async with async_session_maker() as session:
            return await BookingRepository.select_times(
                user_id=user_id, session=session, booking_id=booking_id, time=time
            )
