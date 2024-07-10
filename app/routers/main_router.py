from fastapi import APIRouter, Request, Depends
from app.models.user_model import User
from app.auth.dependencies import get_current_user
from app.utils.templating import templates
from fastapi.responses import HTMLResponse
from app.repository.notification_repo import NotificationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from app.schemas.notification_schemas import NotificationOut


main_router: APIRouter = APIRouter()



@main_router.get('/', status_code=200, name='main:page')
async def get_main_page(request: Request, session: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)) -> HTMLResponse:
    notifications: list[NotificationOut] = await NotificationRepository.find_all_notif(session=session)
    return templates.TemplateResponse(request=request, name='base.html', context={'user': user, 'notifications': notifications})
