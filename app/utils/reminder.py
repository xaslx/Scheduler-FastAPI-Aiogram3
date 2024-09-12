from datetime import date, datetime, time, timedelta


def reminder(time_: str, date: date) -> datetime:
    time_split: list[str] = time_.split(":")

    booking_datetime: datetime = datetime.combine(
        date=date, time=time(hour=int(time_split[0]), minute=int(time_split[1]))
    )
    reminder_time: datetime = booking_datetime - timedelta(hours=2)
    return reminder_time
