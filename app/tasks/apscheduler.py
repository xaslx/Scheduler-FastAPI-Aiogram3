from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.generate_time import moscow_tz
from config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


jobstores: dict[str, SQLAlchemyJobStore] = {
    "default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")
}
scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=moscow_tz, jobstores=jobstores)
