from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.generate_time import moscow_tz
from config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore



jobstores: dict[str, RedisJobStore] = {'default': RedisJobStore(db=2, host=settings.REDIS_HOST, port=settings.REDIS_PORT)}
scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=moscow_tz, jobstores=jobstores)
