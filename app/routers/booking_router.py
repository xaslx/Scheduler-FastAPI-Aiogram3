from fastapi import APIRouter, Depends, Request, Query
from app.utils.templating import templates
from app.repository.booking_repo import BookingRepository
from app.repository.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, get_all_notifications
from database import get_async_session
from app.models.user_model import User
from fastapi.responses import HTMLResponse, JSONResponse
from app.schemas.booking_schemas import BookingDate, BookingTime, BookingOut
from datetime import datetime, date, timedelta, timezone
from app.utils.generate_time import generate_time_intervals
from exceptions import UserNotFound, BookingNotFound
from app.models.booking_model import Booking
from app.schemas.notification_schemas import NotificationOut
from fastapi.responses import RedirectResponse
from typing import Annotated


booking_router: APIRouter = APIRouter(
    prefix='/booking',
    tags=['Запись']
)


@booking_router.get('/{personal_link}', status_code=200, name='personal_link:page')
async def  get_booking_by_link(
    personal_link: str,
    request: Request, 
    user: User = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
    session: AsyncSession = Depends(get_async_session)) -> HTMLResponse:
    user_link: User = await UserRepository.find_one_or_none(session=session, personal_link=personal_link)
    if user_link is None:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user, 'notifications': notifications})
    return templates.TemplateResponse(request=request, name='booking.html', context={'user': user, 'user_link': user_link,  'notifications': notifications})


@booking_router.post('/add_booking', status_code=201)
async def add_booking(
    date_for_booking: BookingDate,
    session: AsyncSession = Depends(get_async_session)
):
    user: User = await UserRepository.find_one_or_none(session=session, id=date_for_booking.user_id)
    date_for = date_for_booking.date_for_booking.date() + timedelta(days=1)
    if not user:
        raise UserNotFound
    intervals = await generate_time_intervals(user.start_time, user.end_time, user.interval)
    booking: BookingOut = await BookingRepository.get_booking(session=session, user_id=date_for_booking.user_id, date=date_for)

    booking_id: int = booking.id if booking else 0

    if not booking:
        booking_id = await BookingRepository.add(session=session, date_for_booking=date_for, user_id=user.id, times=intervals)
    
    redirect_url = booking_router.url_path_for('gettime:page', personal_link=user.personal_link) + f'?date={date_for}&user_id={user.id}&booking_id={booking_id}'
    return JSONResponse(content={"redirect_url": redirect_url}, status_code=200)

@booking_router.get('/{personal_link}/select_time', status_code=200, name='gettime:page')
async def get_time(
    personal_link: str,
    booking_id: Annotated[int, Query()],
    date: Annotated[date, Query()],
    user_id: Annotated[int, Query()],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
    notifications: list = Depends(get_all_notifications)
):
    user_link: User = await UserRepository.find_one_or_none(session=session, personal_link=personal_link)

    if not user_link or user_link.id != user_id or user_link.personal_link != personal_link:
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user, 'notifications': notifications})

    booking: BookingOut = await BookingRepository.find_booking(user_id=user_link.id, date=date, session=session)

    if not booking or (booking.id != booking_id):
        return templates.TemplateResponse(request=request, name='404.html', context={'user': user, 'notifications': notifications})

    return templates.TemplateResponse(request=request, name='select_time.html', 
                                      context={'user': user, 'notifications': notifications, 'selected_times': booking.selected_times, 'times': booking.times, 'booking_id': booking_id})


@booking_router.patch('/edit_booking/{booking_id}', status_code=200)
async def edit_booking(
    booking_id: int, 
    time: Annotated[str, Query()],
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
    ):
 
    booking: BookingOut = await BookingRepository.find_one_or_none(session=session, id=booking_id)
    if not booking:
        raise BookingNotFound
    await BookingRepository.update_times(session=session, user_id=booking.user_id, booking_id=booking.id, time=time)
    
    #здесь будет код
    # await BookingRepository.update_times(user_id=user.id, session=session, booking_id=booking_id)
