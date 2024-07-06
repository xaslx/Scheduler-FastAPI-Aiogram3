from .base_repo import BaseRepository
from app.models.notification_model import Notification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class NotificationRepository(BaseRepository):
    model = Notification


    @classmethod
    async def find_all_notif(cls, session: AsyncSession):
        query = select(cls.model).order_by(cls.model.created_at.desc()).limit(3)
        res = await session.execute(query)
        return res.scalars().all()