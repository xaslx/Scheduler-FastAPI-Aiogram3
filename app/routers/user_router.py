import math
import secrets
from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_password_hash
from app.auth.authentication import generate_token
from app.auth.dependencies import (get_admin_user, get_all_notifications,
                                   get_current_user)
from app.models.user_model import User
from app.repository.booking_repo import BookingRepository
from app.repository.user_repo import UserRepository
from app.schemas.booking_schemas import BookingOut
from app.schemas.notification_schemas import NotificationOut
from app.schemas.user_schema import (EditEnabled, EditPassword, EditRole,
                                     EditTime, ResetPassword, UserOut,
                                     UserUpdate)
from app.tasks.tasks import (password_changed, reset_password_email,
                             update_password)
from app.utils.generate_time import moscow_tz
from app.utils.templating import templates
from database import get_async_session
from exceptions import NotAccessError, UserNotFound
from logger import logger


user_router: APIRouter = APIRouter(prefix="/user", tags=["Пользователи"])


@user_router.get("/my_profile", status_code=200, name="myprofile:page")
async def show_my_profile_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "my_profile.html",
        {"request": request, "user": user, "notifications": notifications},
    )


@user_router.get("/clients", status_code=200, name="clients:page")
async def get_my_clients(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(
            request=request, name="not_logined.html", context={"user": user}
        )
    bookings: BookingOut = await BookingRepository.find_all_booking(
        user_id=user.id, date=datetime.now(tz=moscow_tz).date(), session=session
    )
    return templates.TemplateResponse(
        request=request,
        name="my_clients.html",
        context={"user": user, "notifications": notifications, "clients": bookings},
    )


@user_router.get("/clients/", status_code=200, name="clients_by_date:page")
async def get_my_clients_by_date(
    date: Annotated[date, Query()],
    user_id: Annotated[int, Query()],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    if not user or user.id != user_id:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    booking: BookingOut = await BookingRepository.get_booking(
        user_id=user_id, date=date, session=session
    )
    if not booking:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    return templates.TemplateResponse(
        request=request,
        name="client_by_date.html",
        context={
            "user": user,
            "notifications": notifications,
            "date": booking.date_for_booking,
            "selected_times": booking.selected_times,
            "booking": booking,
        },
    )


@user_router.get("/edit_profile", status_code=200, name="edit:page")
async def get_edit_my_profile_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(
            request=request, name="not_logined.html", context={"user": user}
        )
    return templates.TemplateResponse(
        request=request,
        name="edit_profile.html",
        context={"user": user, "notifications": notifications},
    )


@user_router.get("/edit_password", name="edit_password:page", status_code=200)
async def get_edit_my_password_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:

    if not user:
        return templates.TemplateResponse(
            request=request, name="not_logined.html", context={"user": user}
        )
    return templates.TemplateResponse(
        request=request,
        name="edit_password.html",
        context={"user": user, "notifications": notifications},
    )


@user_router.patch("/edit_password", status_code=200)
async def edit_password(
    response: Response,
    new_password: EditPassword,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
):

    if not user or (user.id != new_password.user_id):
        raise NotAccessError

    hashed_password: str = get_password_hash(new_password.new_password)

    await UserRepository.update(
        session=session, id=new_password.user_id, hashed_password=hashed_password
    )
    logger.info(f'Пользователь: ID={user.id}, email={user.email} изменил свой пароль')
    update_password.delay(
        email=new_password.email, new_password=new_password.new_password
    )
    logger.info(f'Пользователю: ID={user.id}, email={user.email} отправлено письмо с измененным паролем')
    response.delete_cookie("user_access_token")


@user_router.patch("/edit_profile", status_code=200)
async def edit_my_profile(
    new_user: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
):
    if not user:
        logger.warning('Ошибка прав доступа при редактировании профиля')
        raise NotAccessError
    
    await UserRepository.update(
        session=session,
        id=user.id,
        **new_user.model_dump(exclude={"password", "email"}),
    )
    logger.info(f'Пользователь: ID={user.id}, email={user.email} изменил свой профиль')


@user_router.get("/all_users", status_code=200, name="allusers:page")
async def get_all_users(
    request: Request,
    page: Annotated[int, Query()] = 1,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> Page[UserOut]:

    res: Page[UserOut] = await paginate(
        session, select(User).order_by(User.registered_at)
    )

    if user is None or user.role == "user":
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="banned.html",
            context={"user": user, "notifications": notifications},
        )
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "notifications": notifications,
            "pagination": True,
            "user": user,
            "min": min,
            "max": max,
            "users": res.items,
            "total_users": res.total,
            "page": res.page,
            "pages": res.pages,
        },
    )


@user_router.get("/search_user", status_code=200, name="search:page")
async def search_user_by_name_surname(
    request: Request,
    query: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_admin_user),
    page: Annotated[int, Query()] = 1,
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    users: list[User] = []

    if not user:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"user": user}
        )
    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="banned.html",
            context={"user": user, "notifications": notifications},
        )
    if query:
        users: list[UserOut] = await UserRepository.search_user_by_name_surname_or_email(
            session=session, text=query
        )
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "pagination": False,
            "page": page,
            "notifications": notifications,
            "total_users": len(users),
            "users": users,
            "user": user,
            "pages": math.ceil(len(users) / 50),
        },
    )


@user_router.get("/my_settings", status_code=200, name="settings:page")
async def get_my_settings_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(request=request, name="not_logined.html")
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={"user": user, "notifications": notifications},
    )


@user_router.get("/{user_id}", status_code=200, name="user_by_id:page")
async def get_user_by_id(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:

    user_by_id: UserOut = await UserRepository.find_one_or_none(
        id=user_id, session=session
    )

    if not user_by_id or not user:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"user": user}
        )
    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="banned.html",
            context={"user": user, "notifications": notifications},
        )
    return templates.TemplateResponse(
        request=request,
        name="user_by_id.html",
        context={
            "user": user,
            "user_by_id": user_by_id,
            "notifications": notifications,
        },
    )


@user_router.patch("/ban/{user_id}", status_code=200)
async def ban_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin: UserOut = Depends(get_admin_user),
):
    if not admin:
        logger.warning(f'Ошибка прав доступа при блокировке пользователя (не админ)')
        raise NotAccessError
    user: UserOut = await UserRepository.find_one_or_none(id=user_id, session=session)
    if not user:
        raise UserNotFound
    if admin.role == "admin":
        if user_id == admin.id or user.role == "admin":
            logger.warning(f'Ошибка прав доступа при блокировке пользователя')
            raise NotAccessError
    await UserRepository.update(session=session, id=user_id, is_active=False)
    logger.info(f'Администратор: ID={admin.id}, email={admin.email} заблокировал пользователя ID={user.id}, email={user.email}')


@user_router.patch("/unban/{user_id}", status_code=200)
async def unban_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin: UserOut = Depends(get_admin_user),
):
    if not admin:
        logger.warning(f'Ошибка прав доступа при разблокировке пользователя (не админ)')
        raise NotAccessError
    user: UserOut = await UserRepository.find_one_or_none(id=user_id, session=session)
    if not user:
        raise UserNotFound
    if admin.role == "admin" or user.role == "admin":
        if user_id == admin.id:
            logger.warning(f'Ошибка прав доступа при разблокировке пользователя')
            raise NotAccessError
    await UserRepository.update(session=session, id=user_id, is_active=True)
    logger.info(f'Администратор: ID={admin.id}, email={admin.email} разблокировал пользователя ID={user.id}, email={user.email}')


@user_router.patch("/edit_role/{user_id}", status_code=200, name="edit_role:page")
async def edit_role_for_user(
    new_role: EditRole,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin: UserOut = Depends(get_admin_user),
):
    if admin.role == "admin" or not admin:
        logger.warning(f'Ошибка прав доступа при изменении роли пользователя (только для роли dev)')
        raise NotAccessError
    await UserRepository.update(session=session, id=user_id, role=new_role.role)
    logger.info(f'Администратор: ID={admin.id}, email={admin.email} изменил роль пользователю ID={user_id}, новая роль - {new_role.role}')


@user_router.delete(
    "/delete_user_for_admin/{user_id}", status_code=200, name="delete_user:page"
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin: UserOut = Depends(get_admin_user),
):
    user: UserOut = await UserRepository.find_one_or_none(session=session, id=user_id)
    if not user:
        raise UserNotFound
    if admin.role != "dev":
        logger.warning(f'Ошибка прав доступа при удалении пользователя (только для роли dev)')
        raise NotAccessError
    await UserRepository.delete(session=session, id=user_id)
    logger.info(f'Администратор: ID={admin.id}, email={admin.email} удалил пользователя ID={user.id}, email={user.email}')


@user_router.delete("/delete_user/{user_id}", name="del_user:page")
async def del_user(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
    notifications: list[str] = Depends(get_all_notifications),
) -> HTMLResponse:

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    if user.id != user_id:
        logger.warning(f'Ошибка прав доступа при удалении профиля')
        raise NotAccessError
    await UserRepository.delete(session=session, id=user_id)
    logger.info(f'Пользователь ID={user.id}, email={user.email} удалил свой профиль')


@user_router.patch("/edit_enabled/{user_id}")
async def edit_enabled(
    enabled: EditEnabled,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
):
    if not user or user.id != user_id:
        logger.warning('Ошибка прав доступа при изменении возможности записи')
        raise NotAccessError
    await UserRepository.update(session=session, id=user_id, enabled=enabled.enabled)
    logger.info(f'Пользователь ID={user.id}, email={user.email} изменил возможность записи на - {enabled.enabled}')


@user_router.patch("/edit_time/{user_id}")
async def edit_time(
    new_time: EditTime,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
):
    if not user or user.id != user_id:
        logger.warning('Ошибка прав доступа при изменении рабочего дня')
        raise NotAccessError
    await UserRepository.update(
        session=session, id=user_id, **new_time.model_dump(exclude_unset=True)
    )
    logger.info(f'Пользователь ID={user.id}, email={user.email} изменил рабочий день / интервал на: \
                 start={str(new_time.start_time)}, end={str(new_time.end_time)}, interval={new_time.interval}')


@user_router.get("/forgot_password/reset", status_code=200, name="reset:page")
async def get_forgot_password_template(
    request: Request,
    notifications: list[NotificationOut] = Depends(get_all_notifications),
    user: UserOut = Depends(get_current_user),
) -> HTMLResponse:

    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"user": user, "notifications": notifications},
    )


@user_router.get("/reset/reset_password", status_code=200, name="reset_password:page")
async def get_reset_password_template(
    token: str,
    request: Request,
    user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:

    exist_user: UserOut = await get_current_user(async_db=session, token=token)
    if not exist_user:
        return templates.TemplateResponse(
            request=request, name="expire_time.html", context={"user": user}
        )
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "user": user,
            "exist_user": exist_user,
            "notifications": notifications,
        },
    )


@user_router.post("/forgot_password/reset", status_code=200)
async def get_forgot_password_template(
    email: ResetPassword,
    session: AsyncSession = Depends(get_async_session),
):

    exist_user: UserOut = await UserRepository.find_one_or_none(
        session=session, email=email.email
    )
    if not exist_user:
        raise HTTPException(status_code=422, detail="Email не найден")
    token: str = await generate_token(exist_user)
    reset_password_email.delay(exist_user.email, token=token)
    logger.info(f'Пользователь ID={exist_user.id}, email={exist_user.email} письмо с ссылкой для сброса пароля')


@user_router.get(
    "/reset/success_update_password", status_code=200, name="success_update_password"
)
async def get_update_password_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="success_update_password.html",
        context={"user": user, "notifications": notifications},
    )


@user_router.patch("/forgot_password/reset")
async def reset_password(
    user_id: ResetPassword,
    session: AsyncSession = Depends(get_async_session),
):
    new_password: str = secrets.token_hex(10)
    hashed_password: str = get_password_hash(new_password)
    await UserRepository.update(
        id=user_id.user_id, hashed_password=hashed_password, session=session
    )
    logger.info(f'Пользователю ID={user_id.user_id}, email={user_id.email} был установлен новый пароль')
    password_changed.delay(email=user_id.email, new_password=new_password)
    logger.info(f'Пользователю ID={user_id.user_id}, email={user_id.email} отправлено письмо на почту с новым паролем')
