from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.models.user_model import User

from .base_repo import BaseRepository
from logger import logger


class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def search_user_by_name_surname_or_email(
        cls, session: AsyncSession, text: str | None = None
    ):
        try:
            query = select(cls.model.__table__.columns).where(
                or_(
                    cls.model.name.icontains(text),
                    cls.model.surname.icontains(text),
                    cls.model.email.icontains(text),
                )
            )
            res = await session.execute(query)
            return res.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось найти юзера.'
            else:
                msg = 'Unknown Exc: Не удалось найти юзера.'
            logger.error(msg)
            return None
