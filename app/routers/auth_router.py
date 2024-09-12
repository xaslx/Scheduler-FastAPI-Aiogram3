import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import authenticate_user, create_access_token, get_password_hash
from app.auth.dependencies import get_all_notifications, get_current_user
from app.models.user_model import User
from app.repository.user_repo import UserRepository
from app.schemas.notification_schemas import NotificationOut
from app.schemas.user_schema import UserLogin, UserRegister, UserOut
from app.tasks.tasks import register_confirmation_message
from app.utils.templating import templates
from database import get_async_session
from exceptions import UserAlreadyExistsException, UserNotFound
from logger import logger


auth_router: APIRouter = APIRouter(
    prefix="/auth", tags=["Аутентификация и Авторизация"]
)


@auth_router.get("/register", status_code=200)
async def get_register_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "user": user, "notifications": notifications},
    )


@auth_router.post("/register", status_code=201)
async def rigister_user(
    user: UserRegister,
    bg_task: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
) -> int:
    exist_user: UserOut = await UserRepository.find_one_or_none(
        session=session, email=user.email
    )

    if exist_user:
        raise UserAlreadyExistsException

    hashed_password: str = get_password_hash(user.password)
    new_personal_link: str = secrets.token_hex(8)
    new_user: UserOut = await UserRepository.add(
        session=session,
        **user.model_dump(exclude="password"),
        personal_link=new_personal_link,
        hashed_password=hashed_password,
    )
    # register_confirmation_message.delay(email_to=user.email) Celery
    bg_task.add_task(register_confirmation_message, email_to=user.email)
    logger.info(
        f"Новый пользователь зарегистрировался! name={user.name}, surname={user.surname}, email={user.email}"
    )
    return new_user


@auth_router.get("/after_register", status_code=200)
async def after_register_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="after_register.html",
        context={"user": user, "notifications": notifications},
    )


@auth_router.post("/login", status_code=200)
async def login_user(
    response: Response,
    user: UserLogin,
    session: AsyncSession = Depends(get_async_session),
) -> str:
    user: UserOut = await authenticate_user(user.email, user.password, async_db=session)
    if not user:
        raise UserNotFound

    access_token, expire = create_access_token({"sub": user.personal_link})
    max_age = (expire - datetime.utcnow()).total_seconds()

    response.set_cookie(
        "user_access_token", access_token, httponly=True, max_age=max_age, secure=True
    )
    logger.info(
        f"Пользователь вошел в систему: ID={user.id}, name={user.name}, surname={user.surname}"
    )
    return access_token


@auth_router.get("/login", status_code=200)
async def get_login_template(
    request: Request, user: UserOut = Depends(get_current_user)
) -> HTMLResponse:

    return templates.TemplateResponse(
        request=request, name="login.html", context={"user": user}
    )


@auth_router.post("/logout", status_code=200)
async def logout_user(
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    cookies: str | None = request.cookies.get("user_access_token")
    try:
        user: UserOut = await get_current_user(async_db=session, token=cookies)
        response.delete_cookie("user_access_token")
        logger.info(
            f"Пользователь ID={user.id}, name={user.name}, surname={user.surname} вышел из системы"
        )
    except:
        logger.error("Ошибка при выходе из системы")
