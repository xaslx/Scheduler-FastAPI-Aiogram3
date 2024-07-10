from datetime import datetime, timedelta
import pytz
from datetime import datetime


moscow_tz = pytz.timezone('Europe/Moscow')

async def generate_time_intervals(start_time, end_time, interval_minutes) -> list:
    start: datetime = datetime.combine(datetime.today(), start_time)
    end: datetime = datetime.combine(datetime.today(), end_time)

    intervals: list = []
    
    while start.time() < end.time():
        intervals.append(start.time().strftime("%H:%M"))
        start += timedelta(minutes=interval_minutes)
    
    return intervals