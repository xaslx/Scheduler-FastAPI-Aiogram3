from pydantic import BaseModel
from datetime import datetime, date, time




class BookingDate(BaseModel):
    date_for_booking: datetime
    user_id: int
    times: list[str] | None = None

class BookingTime(BaseModel):
    time_booking: time

class BookingOut(BookingDate):
    id: int