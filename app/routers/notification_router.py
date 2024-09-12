from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_admin_user,
    get_all_notifications,
    get_current_user,
)
from app.repository.notification_repo import NotificationRepository
from app.repository.user_repo import UserRepository
from app.schemas.notification_schemas import CreateNotification, NotificationOut
from app.schemas.user_schema import CreateMessage, UserOut
from app.tasks.tasks import send_notification
from app.utils.redis_cache import delete_cache_notifications
from app.utils.templating import templates
from database import get_async_session
from exceptions import NotAccessError, NotificationNotFound
from logger import logger
from redis_init import redis

notification_router: APIRouter = APIRouter(prefix="/notification", tags=["Уведомления"])


@notification_router.get("/all", status_code=200, name="allnotification:page")
async def get_all_notification(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    cached_data = await redis.hgetall("all_notifications")
    if not cached_data:
        all_notifications: list[NotificationOut] = (
            await NotificationRepository.find_all(session=session)
        )
        notifications_out = [
            NotificationOut.model_validate(notif) for notif in all_notifications
        ]
        for notification in notifications_out:
            await redis.hset(
                "all_notifications", notification.id, notification.model_dump_json()
            )
            await redis.expire("all_notifications", 600)
    else:
        all_notifications: list[NotificationOut] = [
            NotificationOut.model_validate_json(value) for value in cached_data.values()
        ]

    return templates.TemplateResponse(
        request=request,
        name="all_notifications.html",
        context={
            "user": user,
            "all_notifications": sorted(
                all_notifications, key=lambda notif: notif.created_at, reverse=True
            ),
            "notifications": notifications,
        },
    )


@notification_router.get("/create", status_code=200, name="createnot:page")
async def get_create_notification_template(
    request: Request,
    user: UserOut = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    return templates.TemplateResponse(
        request=request,
        name="create_notification.html",
        context={"user": user, "notifications": notifications},
    )


@notification_router.get(
    "/create_notification_email", status_code=200, name="create_notification:page"
)
async def get_create_notification_email_template(
    request: Request,
    user: UserOut = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"user": user}
        )
    return templates.TemplateResponse(
        request=request,
        name="create_notification_email.html",
        context={"user": user, "notifications": notifications},
    )


@notification_router.get(
    "/create_notification_website", status_code=200, name="create_notification_web:page"
)
async def get_create_notification_website_template(
    request: Request,
    user: UserOut = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"user": user}
        )
    return templates.TemplateResponse(
        request=request,
        name="create_notification_website.html",
        context={"user": user, "notifications": notifications},
    )


@notification_router.get("/{notif_id}", status_code=200)
async def get_notification_by_id(
    request: Request,
    notif_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    notification: NotificationOut = await NotificationRepository.find_one_or_none(
        session=session, id=notif_id
    )
    if not notification:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    return templates.TemplateResponse(
        request=request,
        name="notification_by_id.html",
        context={
            "user": user,
            "notification": notification,
            "notifications": notifications,
        },
    )


@notification_router.post("/create_notification_for_website", status_code=201)
async def create_notification(
    new_notification: CreateNotification,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_admin_user),
):

    if not user:
        logger.warning(f"Ошибка прав доступа при добавлении уведомления")
        raise NotAccessError

    notifications: list[NotificationOut] = await NotificationRepository.find_all(
        session=session
    )

    if len(notifications) >= 30:
        await NotificationRepository.delete(session=session, id=notifications[0].id)
        logger.info("Удаление последнего уведомления из базы данных")

    await NotificationRepository.add(session=session, **new_notification.model_dump())
    logger.info(
        f"Администратор: ID={user.id}, email={user.email} добавил новое уведомление на сайт (в бд)"
    )
    await delete_cache_notifications()
    return status.HTTP_201_CREATED


@notification_router.post("/send_notification_email", status_code=200)
async def send_notification_for_all_users(
    message: CreateMessage,
    bg_task: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_admin_user),
):
    if not user:
        logger.warning(f"Ошибка прав доступа при отправке уведомлений на email")
        raise NotAccessError

    users: list[UserOut] = await UserRepository.find_all(session=session)
    emails: list[str] = [user.email for user in users]
    # send_notification.delay(users=emails, message=message.message) Celery
    bg_task.add_task(send_notification, users=emails, message=message.message)
    logger.info(
        f"Администратор: ID={user.id}, email={user.email} отправил уведомление на email пользователям: кол-во пользователей: {len(emails)}"
    )
    return {"user_count": len(emails)}


@notification_router.delete("/{notif_id}")
async def delete_notification(
    notif_id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_admin_user),
):
    notification: NotificationOut = await NotificationRepository.find_one_or_none(
        session=session, id=notif_id
    )
    if not notification:
        raise NotificationNotFound
    if not user:
        logger.warning(f"Ошибка прав доступа при удалении уведомления")
        raise NotAccessError
    await NotificationRepository.delete(session=session, id=notif_id)
    logger.info(
        f"Администратор ID={user.id}, email={user.email} удалил уведомление на сайте (из бд)"
    )
    await delete_cache_notifications()
