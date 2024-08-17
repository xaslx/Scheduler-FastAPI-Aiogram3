from database import async_session_maker
from sqlalchemy import select, insert
from app.models.telegram_model import Telegram
from app.schemas.tg_schema import TelegramOut


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
    