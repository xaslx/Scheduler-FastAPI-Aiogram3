from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_model import Notification

from .base_repo import BaseRepository


class NotificationRepository(BaseRepository):
    model = Notification

    @classmethod
    async def find_all_notif(cls, session: AsyncSession):
        query = select(cls.model).order_by(cls.model.created_at.desc()).limit(3)
        res = await session.execute(query)
        return res.scalars().all()
