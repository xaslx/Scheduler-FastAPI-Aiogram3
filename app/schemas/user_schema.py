from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    Field,
    ConfigDict,
    model_validator,
)
from datetime import datetime, time
import re
from exceptions import IncorrectNameOrSurnameException

PASSWORD_CHECK = re.compile(r"^[a-zA-Z0-9_-]{6,30}$")
TELEGRAM_CHECK = re.compile(r"^[a-zA-Z0-9_@]{5,15}$")


class BaseValidators(BaseModel):
    @model_validator(mode="before")
    def check_name_and_surname(cls, value: str):
        name = value.get("name")
        surname = value.get("surname")
        if name and " " in name:
            raise HTTPException(
                status_code=422, detail="Имя не может содержать пробелы."
            )
        if surname and " " in surname:
            raise HTTPException(
                status_code=422, detail="Фамилия не может содержать пробелы."
            )
        if name:
            value["name"] = name.capitalize()
        if surname:
            value["surname"] = surname.capitalize()
        return value

    @model_validator(mode="before")
    def check_password(cls, value):
        password = value.get("password")
        if password and not PASSWORD_CHECK.match(password):
            raise HTTPException(
                status_code=422,
                detail="Пароль должен содержать только [англ.букв, цифры 0-9, знак _ -], быть минимум 6 символов и не должен превышать 30 символов.",
            )
        return value

    @model_validator(mode="before")
    def check_new_password(cls, value):
        password = value.get("new_password")
        if password and not PASSWORD_CHECK.match(password):
            raise HTTPException(
                status_code=422,
                detail="Пароль должен содержать только [англ.букв, цифры 0-9, знак _ -], быть минимум 6 символов и не должен превышать 30 символов.",
            )
        return value

    @model_validator(mode="before")
    def repeat_new_password(cls, value):
        password = value.get("repeat_password")
        if password and not PASSWORD_CHECK.match(password):
            raise HTTPException(
                status_code=422,
                detail="Пароль должен содержать только [англ.букв, цифры 0-9, знак _ -], быть минимум 6 символов и не должен превышать 30 символов.",
            )
        return value

    @model_validator(mode="before")
    def check_telegram_link(cls, value):
        telegram_link = value.get("telegram_link")
        if telegram_link and not TELEGRAM_CHECK.match(telegram_link):
            raise HTTPException(
                status_code=422,
                detail="Имя пользователя в телеграм должно содержать только [англ.букв, цифры 0-9, знак _], быть минимум 5 символов и не должно превышать 15 символов.",
            )
        return value


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    profile_photo: str
    role: str
    telegram_link: str | None
    personal_link: str
    registered_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseValidators):
    name: str = Field(min_length=2, max_length=15)
    surname: str = Field(min_length=2, max_length=15)
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6, max_length=20)
    telegram_link: str | None = Field(min_length=5, max_length=15, default=None)


class UserUpdate(BaseValidators):
    name: str | None
    surname: str | None
    telegram_link: str | None
    description: str | None = Field(max_length=500, default=None)


class UserLogin(BaseValidators):
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

    @field_validator("interval")
    def validate_interval(cls, value: int):
        if value < 10 or type(value) != int:
            return 10
        return value


class ResetPassword(BaseModel):
    email: EmailStr
    user_id: int | None = None


class EditPassword(BaseValidators):
    user_id: int
    email: EmailStr
    new_password: str
    repeat_password: str


class CreateMessage(BaseModel):
    message: str = Field(max_length=500)
