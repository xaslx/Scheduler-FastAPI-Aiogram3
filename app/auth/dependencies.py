from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.notification_schemas import NotificationOut
from config import settings
from database import get_async_session
from exceptions import (
    IncorrectTokenException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotAdmin,
    UserIsNotPresentException,
)
from app.models.user_model import User
from app.repository.user_repo import UserRepository
from app.repository.notification_repo import NotificationRepository


def get_token(request: Request):
    token: str = request.cookies.get("user_access_token")
    if not token:
        return None
    return token


async def get_current_user(
    async_db: AsyncSession = Depends(get_async_session),
    token: str = Depends(get_token),
) -> User:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except ExpiredSignatureError:
        return None
    except JWTError:
        raise IncorrectTokenException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UserRepository.find_one_or_none(id=int(user_id), session=async_db)
    if not user:
        return None
    return user


async def get_admin_user(user: User = Depends(get_current_user)):
    role = ["admin", "dev"]
    if user:
        if user.role not in role:
            raise UserIsNotAdmin
        return user
    return None


async def get_all_notifications(session: AsyncSession = Depends(get_async_session)):
    notifications: list[NotificationOut] = await NotificationRepository.find_all_notif(
        session=session
    )
    return notifications
