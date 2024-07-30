from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_all_notifications, get_current_user
from app.models.user_model import User
from app.repository.notification_repo import NotificationRepository
from app.schemas.help_schemas import GetHelp
from app.schemas.notification_schemas import NotificationOut
from app.schemas.user_schema import UserOut
from app.tasks.tasks import help_message
from app.utils.templating import templates
from database import get_async_session
from exceptions import NotAccessError
from logger import logger


main_router: APIRouter = APIRouter()


@main_router.get("/", status_code=200, name="main:page")
async def get_main_page(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
) -> HTMLResponse:
    notifications: list[NotificationOut] = await NotificationRepository.find_all_notif(
        session=session
    )
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"user": user, "notifications": notifications},
    )


@main_router.get("/help", status_code=200, name="help:page")
async def get_help_template(
    request: Request,
    user: UserOut = Depends(get_current_user),
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
        name="help.html",
        context={"user": user, "notifications": notifications},
    )


@main_router.post("/help", status_code=200)
async def get_help(help: GetHelp, user: UserOut = Depends(get_current_user)):
    if not user:
        raise NotAccessError
    help_message.delay(email=help.email, description=help.description)
    logger.info(f'Пользователь {help.email} оставил запрос на "Помощь"')
