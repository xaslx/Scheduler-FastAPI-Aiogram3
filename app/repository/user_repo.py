from .base_repo import BaseRepository
from app.models.user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_



class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def search_user_by_name_surname_or_email(cls, session: AsyncSession, text: str | None = None):
        query = select(cls.model.__table__.columns).where(
            or_(
                cls.model.name.icontains(text),
                cls.model.surname.icontains(text),
                cls.model.email.icontains(text)
        ))
        res = await session.execute(query)
        return res.mappings().all()