from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_model import Notification
from logger import logger

from .base_repo import BaseRepository


class NotificationRepository(BaseRepository):
    model = Notification

    @classmethod
    async def find_all_notif(cls, session: AsyncSession):
        try:
            query = (
                select(cls.model.__table__.columns)
                .order_by(desc(cls.model.created_at))
                .limit(3)
            )
            res = await session.execute(query)
            return res.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Не удалось найти уведомление."
            else:
                msg = "Unknown Exc: Не удалось найти уведомление."
            logger.error(msg)
            return None
