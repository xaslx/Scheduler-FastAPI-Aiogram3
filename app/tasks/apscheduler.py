from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.generate_time import moscow_tz


scheduler: AsyncIOScheduler = AsyncIOScheduler()
scheduler.configure(timezone=moscow_tz)