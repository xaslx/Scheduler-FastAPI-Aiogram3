from pydantic import BaseModel, ConfigDict
from datetime import datetime, date, time




class BookingDate(BaseModel):
    date_for_booking: datetime
    user_id: int
    times: list[str] | None = None
    

class BookingTime(BaseModel):
    time_booking: time

class BookingOut(BookingDate):
    id: int
    selected_times: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)