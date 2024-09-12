from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.utils.generate_time import moscow_tz
from config import settings

jobstores: dict[str, SQLAlchemyJobStore] = {
    "default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")
}
scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=moscow_tz, jobstores=jobstores)
