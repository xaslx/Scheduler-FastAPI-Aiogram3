from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from datetime import datetime, time
import re
from exceptions import IncorrectNameOrSurnameException

PASSWORD_CHECK = re.compile(r"^[a-zA-Z0-9_]{6,20}$")
TELEGRAM_CHECK = re.compile(r"^[a-zA-Z0-9_@]{4,15}$")

class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    profile_photo: str
    role: str
    telegram_link: str
    personal_link: str
    registered_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=15)
    surname: str = Field(min_length=2, max_length=15)
    email: EmailStr = Field(max_length=30)
    password: str
    telegram_link: str | None = Field(min_length=4, max_length=15, default=None)

    @field_validator("name")
    def validate_name(cls, value: str):
        if " " in value:
            raise IncorrectNameOrSurnameException
        return value
    
    @field_validator("surname")
    def validate_surname(cls, value: str):
        if " " in value:
            raise IncorrectNameOrSurnameException
        return value

    @field_validator("password")
    def validate_password(cls, value: str):
        if not PASSWORD_CHECK.match(str(value)):
            raise HTTPException(
                status_code=422,
                detail=f"Пароль должен содержать только [англ.букв, цифры 0-9, знак _], быть минимум 6 символов "
                f"и не должен превышать 20 символов",
            )
        return value
    
    @field_validator("telegram_link")
    def validate_telegram_link(cls, value: str):
        if not TELEGRAM_CHECK.match(str(value)):
            raise HTTPException(
                status_code=422,
                detail=f"Имя пользователя в телеграм должно содержать только [англ.букв, цифры 0-9, знак _], быть минимум 4 символа "
                f"и не должно превышать 15 символов",
            )
        return value

class UserUpdate(BaseModel):
    name: str | None
    surname: str | None
    telegram_link: str | None
    description: str | None = Field(max_length=500, default=None)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class EditRole(BaseModel):
    role: str

class EditEnabled(BaseModel):
    enabled: bool

class EditTime(BaseModel):
    start_time: time
    end_time: time
    interval: int

    @field_validator('interval')
    def validate_interval(cls, value: int):
        if value < 10 or type(value) != int:
            return 10
        return value
    

class ResetPassword(BaseModel):
    email: EmailStr
    user_id: int | None = None


class EditPassword(BaseModel):
    user_id: int
    email: EmailStr
    new_password: str
    repeat_password: str

class CreateMessage(BaseModel):
    message: str = Field(max_length=500)