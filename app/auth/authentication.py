from datetime import datetime, timedelta

from jose import jwt

from app.models.user_model import User
from config import settings


async def generate_token(user: User):
    expire = datetime.utcnow() + timedelta(minutes=5)
    user_to_email = {"sub": str(user.id), "exp": expire}
    token = jwt.encode(user_to_email, settings.SECRET_KEY, settings.ALGORITHM)
    return token


async def generate_token_connect_tg(user_tg_id: str):
    expire = datetime.utcnow() + timedelta(minutes=5)
    user = {"sub": user_tg_id, "exp": expire}
    token = jwt.encode(user, settings.SECRET_KEY, settings.ALGORITHM)
    return token
