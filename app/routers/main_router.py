from fastapi import APIRouter, Request, Depends
from app.models.user_model import User
from app.auth.dependencies import get_current_user
from app.auth.dependencies import get_all_notifications
from app.schemas.help_schemas import GetHelp
from app.utils.templating import templates
from fastapi.responses import HTMLResponse
from app.repository.notification_repo import NotificationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from app.schemas.notification_schemas import NotificationOut
from exceptions import NotAccessError
from app.tasks.tasks import help_message

main_router: APIRouter = APIRouter()



@main_router.get('/', status_code=200, name='main:page')
async def get_main_page(request: Request, session: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)) -> HTMLResponse:
    notifications: list[NotificationOut] = await NotificationRepository.find_all_notif(session=session)
    return templates.TemplateResponse(request=request, name='base.html', context={'user': user, 'notifications': notifications})

@main_router.get('/help', status_code=200, name='help:page')
async def get_help_template(
    request: Request,
    user: User = Depends(get_current_user),
    notifications: NotificationOut = Depends(get_all_notifications)
    ) -> HTMLResponse:
    if not user:
         return templates.TemplateResponse(request=request, name='404.html', context={'user': user, 'notifications': notifications})
    return templates.TemplateResponse(request=request, name='help.html', context={'user': user, 'notifications': notifications})

@main_router.post('/help', status_code=200)
async def get_help(
    help: GetHelp,
    user: User = Depends(get_current_user)
    ):
        if not user:
            raise NotAccessError
        help_message.delay(email=help.email, description=help.description)
        