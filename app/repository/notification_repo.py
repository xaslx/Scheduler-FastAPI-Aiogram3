from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.notification_model import Notification

from .base_repo import BaseRepository
from logger import logger

class NotificationRepository(BaseRepository):
    model = Notification

    @classmethod
    async def find_all_notif(cls, session: AsyncSession):
        try:
            query = select(cls.model).order_by(cls.model.created_at.desc()).limit(3)
            res = await session.execute(query)
            return res.scalars().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось найти уведомление.'
            else:
                msg = 'Unknown Exc: Не удалось найти уведомление.'
            logger.error(msg)
            return None
        
    
