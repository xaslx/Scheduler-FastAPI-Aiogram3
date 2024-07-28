from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
    name: str = Field(min_length=2, max_length=20)
    time: str
    email: EmailStr
    tg: str | None = None
    phone_number: str

    @field_validator("phone_number")
    def check_phone(cls, value: str):
        if not value.isdigit():
            raise ValueError("Телефона должен состоять только из цифр")
        return value
