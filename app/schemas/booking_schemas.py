from pydantic import BaseModel, ConfigDict, EmailStr, Field
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

    
class CancelBooking(BaseModel):
    date: str
    time: str
    email: EmailStr
    description: str = Field(min_length=10, max_length=200)

class CreateBooking(BaseModel):
    time: str
    email: EmailStr
    tg: str | None = None
    phone_number: str