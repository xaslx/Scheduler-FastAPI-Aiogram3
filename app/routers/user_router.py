from fastapi import APIRouter, Depends, Request, Query, Response
from pydantic import EmailStr
from app.auth.auth import get_password_hash
from database import get_async_session
from app.auth.dependencies import get_current_user, get_admin_user
from app.repository.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from app.models.user_model import User
from app.schemas.user_schema import UserOut, UserUpdate, EditRole, EditEnabled, EditTime, ResetPassword, EditPassword, CreateMessage
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from exceptions import UserNotFound, NotAccess
from app.utils.templating import templates
from typing import Annotated
from fastapi.exceptions import HTTPException
from app.tasks.tasks import reset_password_email, password_changed, update_password, send_notification
import secrets
from app.auth.authentication import generate_token
from app.schemas.jwt_token import Token


user_router: APIRouter = APIRouter(
    prefix='/user',
    tags=['Пользователи']
)



@user_router.get('/my_profile', status_code=200, name='myprofile:page')
async def show_my_profile_template(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    return templates.TemplateResponse('my_profile.html', {'request': request, 'user': user})

@user_router.get('/edit_profile', status_code=200, name='edit:page')
async def get_edit_my_profile_template(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='edit_profile.html', context={'user': user})

@user_router.get('/create_notification', status_code=200, name='create_notification:page')
async def get_create_notification_template(
    request: Request,
    user: User = Depends(get_admin_user)
) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='create_notification.html', context={'user': user})

@user_router.post('/send_notification', status_code=200)
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
    

@user_router.get('/edit_password', status_code=200, name='edit_password:page')
async def get_edit_my_password_template(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(request=request, name='not_logined.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='edit_password.html', context={'user': user})

@user_router.patch('/edit_password', status_code=200)
async def edit_password(
    response: Response,
    new_password: EditPassword,
    session: AsyncSession = Depends(get_async_session)):
    print(new_password)
    if new_password.new_password != new_password.repeat_password:
        raise HTTPException(
            status_code=422,
            detail='Пароли не совпадают'
        )  
    hashed_password: str = get_password_hash(new_password.new_password)

    await UserRepository.update(session=session, id=new_password.user_id, hashed_password=hashed_password)
    update_password.delay(email=new_password.email, new_password=new_password.new_password)
    response.delete_cookie("user_access_token")



@user_router.patch('/edit_profile', status_code=201)
async def edit_my_profile(new_user: UserUpdate, session: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    await UserRepository.update(session=session, id=user.id, **new_user.model_dump())

@user_router.get('/all_users', status_code=200, name='allusers:page')
async def get_all_users(
    request: Request, 
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(get_admin_user)) -> HTMLResponse:
    users: list[UserOut] = await UserRepository.find_all(session=session)
    if user is None or user.role == 'user':
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user})
    if not user.is_active:
        return templates.TemplateResponse(request=request, name='banned.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='all_users.html', context={'users': users, 'user': user})

@user_router.get('/search_user', status_code=200, name='search:page')
async def search_user_by_name_surname(
    request: Request,
    query: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_admin_user)
) -> HTMLResponse:
    users: list[User] = []

    if not user:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user})
    if query:
        users: list[User] = await UserRepository.search_user_by_name_surname_or_email(session=session, text=query)
    if not user.is_active:
        return templates.TemplateResponse(request=request, name='banned.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='all_users.html', context={'users': users, 'user': user})

@user_router.get('/my_settings', status_code=200, name='settings:page')
async def get_my_settings_template(
    request: Request,
    user: User = Depends(get_current_user)
    ) -> HTMLResponse:
    if not user:
        return templates.TemplateResponse(request=request, name='not_logined.html')
    return templates.TemplateResponse(request=request, name='settings.html', context={'user': user})

@user_router.get('/{user_id}', status_code=200, name='user_by_id:page')
async def get_user_by_id(
    request: Request,
    user_id: int, 
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(get_admin_user)) -> HTMLResponse:

    user_by_id: User = await UserRepository.find_one_or_none(id=user_id, session=session)  

    if not user_by_id or not user:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user})
    if not user.is_active:
        return templates.TemplateResponse(request=request, name='banned.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='user_by_id.html', context={'user': user, 'user_by_id': user_by_id})


@user_router.patch('/ban/{user_id}', status_code=200)
async def ban_user(user_id: int, session: AsyncSession = Depends(get_async_session), admin: User = Depends(get_admin_user)):
    user: User = await UserRepository.find_one_or_none(id=user_id, session=session)
    if not user:
        raise UserNotFound
    if admin.role == 'admin':
        if user_id == admin.id or user.role == 'admin':
            raise NotAccess
    await UserRepository.update(session=session, id=user_id, is_active=False)


@user_router.patch('/unban/{user_id}', status_code=200)
async def unban_user(user_id: int, session: AsyncSession = Depends(get_async_session), admin: User = Depends(get_admin_user)):
    user: User = await UserRepository.find_one_or_none(id=user_id, session=session)
    if not user:
        raise UserNotFound
    if admin.role == 'admin' or user.role == 'admin':
        if user_id == admin.id:
            raise NotAccess
    await UserRepository.update(session=session, id=user_id, is_active=True)

@user_router.patch('/edit_role/{user_id}', status_code=200, name='edit_role:page')
async def edit_role_for_user(
    new_role: EditRole,
    user_id: int, 
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_admin_user)
    ):
    if admin.role == 'admin':
        raise NotAccess
    await UserRepository.update(session=session, id=user_id, role=new_role.role)

@user_router.delete('/delete_user/{user_id}', status_code=200, name='delete_user:page')
async def delete_user(user_id: int, session: AsyncSession = Depends(get_async_session), admin: User = Depends(get_admin_user)):
    user: User = await UserRepository.find_one_or_none(session=session, id=user_id)
    if not user:
        raise UserNotFound
    if admin.role != 'dev':
        raise NotAccess
    await UserRepository.delete(session=session, id=user_id)

@user_router.patch('/edit_enabled/{user_id}')
async def edit_enabled(
    enabled: EditEnabled,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)                  
    ):
    if user is None:
        return templates.TemplateResponse()
    await UserRepository.update(session=session, id=user_id, enabled=enabled.enabled)


@user_router.patch('/edit_time/{user_id}')
async def edit_time(
    new_time: EditTime,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)
):
    
    await UserRepository.update(session=session, id=user_id, **new_time.model_dump(exclude_unset=True))


@user_router.get('/forgot_password/reset', status_code=200, name='reset:page')
async def get_forgot_password_template(
    request: Request, 
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(get_current_user)) -> HTMLResponse:

    return templates.TemplateResponse(request=request, name='forgot_password.html', context={'user': user})

@user_router.get('/reset/reset_password', status_code=200, name='reset_password:page')
async def get_reset_password_template(
    token: str, 
    request: Request, 
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)) -> HTMLResponse:

    exist_user = await get_current_user(async_db=session, token=token)
    print(exist_user)
    if not exist_user:
        return templates.TemplateResponse(request=request, name='expire_time.html', context={'user': user})
    return templates.TemplateResponse(request=request, name='reset_password.html', context={'user': user, 'exist_user': exist_user})

@user_router.post('/forgot_password/reset', status_code=200)
async def get_forgot_password_template(
    email: ResetPassword,
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(get_current_user)):

    exist_user: User = await UserRepository.find_one_or_none(session=session, email=email.email)
    if not exist_user:
        raise HTTPException(
            status_code=422,
            detail='Email не найден'
        )
    token: str = await generate_token(exist_user)
    reset_password_email.delay(exist_user.email, token=token)


@user_router.get('/reset/success_update_password', status_code=200, name='success_update_password')
async def get_update_password_template(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='success_update_password.html', context={'user': user})

@user_router.patch("/forgot_password/reset")
async def reset_password(
    user_id: ResetPassword,
    session: AsyncSession = Depends(get_async_session),
):
    new_password: str = secrets.token_hex(10)
    hashed_password: str = get_password_hash(new_password)
    await UserRepository.update(id=user_id.user_id, hashed_password=hashed_password, session=session)
    password_changed.delay(email=user_id.email, new_password=new_password)
    return JSONResponse(content={"message": "Password successfully updated"})
