from fastapi import APIRouter, Depends, Request, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select, desc
from app.auth.dependencies import get_current_user, get_admin_user, get_all_notifications
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repo import UserRepository
from app.repository.notification_repo import NotificationRepository
from app.schemas.user_schema import CreateMessage
from app.tasks.tasks import send_notification
from database import get_async_session
from app.models.user_model import User
from app.schemas.notification_schemas import CreateNotification, NotificationOut
from exceptions import NotAccess
from app.utils.templating import templates
from typing import Annotated
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from app.models.notification_model import Notification
from app.schemas.notification_schemas import NotificationOut
from exceptions import NotificationNotFound


notification_router: APIRouter = APIRouter(
    prefix='/notification',
    tags=['Уведомления']
)


@notification_router.get('/all', status_code=200, name='allnotification:page')
async def get_all_notification(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    page: Annotated[int, Query()] = 1,
    user: User = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications)
    ) -> Page[NotificationOut]:
    res =  await paginate(session, select(Notification).order_by(desc(Notification.created_at)))
    if not user:
        return templates.TemplateResponse(request=request, name='not_logined.html', context={'user': user})
    return templates.TemplateResponse(
        request=request, 
        name='all_notifications.html', 
        context={'user': user, 'all_notifications': res.items, 'total': res.total, 'page': page, 'pages': res.pages, 'notifications': notifications})


@notification_router.get('/create', status_code=200, name='createnot:page')
async def get_create_notification_template(
    request: Request, 
    user: User = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications)
    ) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='create_notification.html', context={'user': user, 'notifications': notifications})

@notification_router.get('/create_notification_email', status_code=200, name='create_notification:page')
async def get_create_notification_email_template(
    request: Request,
    user: User = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications)
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='create_notification_email.html', context={'user': user, 'notifications': notifications})

@notification_router.get('/create_notification_website', status_code=200, name='create_notification_web:page')
async def get_create_notification_website_template(
    request: Request,
    user: User = Depends(get_admin_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications)
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='create_notification_website.html', context={'user': user, 'notifications': notifications})

@notification_router.get('/{notif_id}', status_code=200)
async def get_notification_by_id(
    request: Request, 
    notif_id: int, 
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications)
    ) -> HTMLResponse:
    notification: NotificationOut = await NotificationRepository.find_one_or_none(session=session, id=notif_id)
    if not notification:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user, 'notifications': notifications})
    return templates.TemplateResponse(request=request, name='notification_by_id.html', context={'user': user, 'notification': notification, 'notifications': notifications})

@notification_router.post('/create_notification_for_website', status_code=201)
async def create_notification(
    new_notification: CreateNotification,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_admin_user)
):
    if not user:
        raise NotAccess
    
    notifications: list[NotificationOut] = await NotificationRepository.find_all(session=session)
    if len(notifications) >= 30:
        await NotificationRepository.delete(session=session, id=notifications[0].id)
    await NotificationRepository.add(session=session, **new_notification.model_dump())
    return status.HTTP_201_CREATED
    

@notification_router.post('/send_notification_email', status_code=200)
async def send_notification_for_all_users(
    message: CreateMessage,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_admin_user)
):
    if not user:
        raise NotAccess
    
    users: list[User] = await UserRepository.find_all(session=session)
    emails: list[str] = [user.email for user in users]
    send_notification.delay(users=emails, message=message.message)
    return {"user_count": len(emails)}

@notification_router.delete('/{notif_id}')
async def delete_notification(
    notif_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_admin_user)                    
    ):
    notification: NotificationOut = await NotificationRepository.find_one_or_none(session=session, id=notif_id)
    if not notification:
        raise NotificationNotFound
    if not user:
        raise NotAccess
    await NotificationRepository.delete(session=session, id=notif_id)
