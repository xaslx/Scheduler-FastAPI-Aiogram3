from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from logger import logger


class BaseRepository:
    model = None

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        try:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось найти обьект.'
            else:
                msg = 'Unknown Exc: Не удалось найти обьект.'
            logger.error(msg)
            return None


    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        try:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось найти обьекты.'
            else:
                msg = 'Unknown Exc: Не удалось найти обьекты.'
            logger.error(msg)
            return None

    @classmethod
    async def add(cls, session: AsyncSession, **data):
        try:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось добавить обьект.'
            else:
                msg = 'Unknown Exc: Не удалось добавить обьект.'
            logger.error(msg)
            return None

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **data):
        try:
            query = update(cls.model).filter_by(id=id).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось обновить обьект.'
            else:
                msg = 'Unknown Exc: Не удалось обновить обьект.'
            logger.error(msg)
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, id: int):
        try:
            query = delete(cls.model).filter_by(id=id).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = 'Database Exc: Не удалось удалить обьект.'
            else:
                msg = 'Unknown Exc: Не удалось удалить обьект.'
            logger.error(msg)
            return None