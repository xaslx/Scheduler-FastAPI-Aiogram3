from fastapi import APIRouter, Request, Depends
from app.models.user_model import User
from app.auth.dependencies import get_current_user
from app.utils.templating import templates
from fastapi.responses import HTMLResponse


main_router: APIRouter = APIRouter()



@main_router.get('/', status_code=200, name='main:page')
async def get_main_page(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='base.html', context={'user': user})
