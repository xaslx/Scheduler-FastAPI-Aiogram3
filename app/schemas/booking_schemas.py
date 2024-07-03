from pydantic import BaseModel
from datetime import datetime, date, time




class BookingDate(BaseModel):
    date_for_booking: datetime
    user_id: int

class BookingTime(BaseModel):
    time_booking: time