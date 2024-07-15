from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, delete, insert



class BaseRepository:
    model = None

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model.__table__.columns).filter_by(**filter_by)
        result = await session.execute(query)
        return result.mappings().one_or_none()

    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        query = select(cls.model.__table__.columns).filter_by(**filter_by)
        result = await session.execute(query)
        return result.mappings().all()
    
    @classmethod
    async def add(cls, session: AsyncSession, **data):
        query = insert(cls.model).values(**data).returning(cls.model.id)
        result = await session.execute(query)
        await session.commit()
        return result.scalar()

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **data):
        query = update(cls.model).filter_by(id=id).values(**data).returning(cls.model)
        result = await session.execute(query)
        await session.commit()
        return result.scalar()
    
    
    
    @classmethod
    async def delete(cls, session: AsyncSession, id: int):
        query = delete(cls.model).filter_by(id=id).returning(cls.model)
        result = await session.execute(query)
        await session.commit()
        return result.scalar()





