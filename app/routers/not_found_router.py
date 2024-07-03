from fastapi.exceptions import HTTPException
from fastapi import Request, Depends, APIRouter
from app.utils.templating import templates
from app.models.user_model import User
from app.auth.dependencies import get_current_user
from fastapi.responses import HTMLResponse


not_found: APIRouter = APIRouter(
    prefix='/error',
    tags=['Ошибка пути']
)


@not_found.get('/not_found')
async def get_error_template(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='404.html', context={'user': user})