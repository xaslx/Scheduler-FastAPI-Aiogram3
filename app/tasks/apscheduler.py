from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.generate_time import moscow_tz
from config import settings
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore



jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

scheduler: AsyncIOScheduler = AsyncIOScheduler()
scheduler.configure(timezone=moscow_tz, jobstores=jobstores)
