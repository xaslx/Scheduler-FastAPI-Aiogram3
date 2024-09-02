from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.repository.notification_repo import NotificationRepository
from app.repository.user_repo import UserRepository
from app.schemas.notification_schemas import NotificationOut
from app.schemas.user_schema import UserOut
from app.utils.redis_cache import get_notifications
from config import settings
from database import get_async_session
from exceptions import (IncorrectTokenException, UserIsNotAdmin,
                        UserIsNotPresentException)
from redis_init import redis



def get_token(request: Request):
    token: str = request.cookies.get("user_access_token")
    if not token:
        return None
    return token


def valid_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except ExpiredSignatureError:
        return None
    except JWTError:
        raise IncorrectTokenException
    return payload


async def get_current_user(
    async_db: AsyncSession = Depends(get_async_session),
    token: str = Depends(get_token),
) -> User:
    if not token:
        return None
    payload = valid_token(token=token)
    user_personal_link: str = payload.get("sub")
    user_data: None | str = await redis.get(user_personal_link)
    if user_data:
        user: UserOut = UserOut.model_validate_json(user_data)
    else:
        user: User = await UserRepository.find_one_or_none(personal_link=user_personal_link, session=async_db)
        user_out = UserOut.model_validate(user)
        if user:
            await redis.set(user_personal_link, user_out.model_dump_json(), ex=600) 

    if not user_personal_link:
        raise UserIsNotPresentException
    if not user:
        return None
    return user


async def get_tg_id(token: str):
    payload = valid_token(token=token)
    if not payload:
        return None
    tg_id: int = int(payload.get('sub'))
    return tg_id


async def get_admin_user(user: User = Depends(get_current_user)):
    role = ["admin", "dev"]
    if user:
        if user.role not in role:
            raise UserIsNotAdmin
        return user
    return None


async def get_all_notifications(session: AsyncSession = Depends(get_async_session)):
    notifications_out: list[NotificationOut] = await get_notifications(session=session)
    return notifications_out