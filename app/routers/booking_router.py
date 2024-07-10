from fastapi import APIRouter, Depends, Request
from app.utils.templating import templates
from app.repository.booking_repo import BookingRepository
from app.repository.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, get_all_notifications
from database import get_async_session
from app.models.user_model import User
from fastapi.responses import HTMLResponse
from app.schemas.booking_schemas import BookingDate, BookingTime
from datetime import datetime, date
from app.utils.generate_time import generate_time_intervals
from exceptions import UserNotFound
from app.models.booking_model import Booking
from app.schemas.notification_schemas import NotificationOut



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

    if not user:
        raise UserNotFound
    if user.date_for_booking is None or (date_for_booking.date_for_booking.date() not in user.date_for_booking):
        intervals: list[str] = await generate_time_intervals(user.start_time, user.end_time, user.interval)
        res = await BookingRepository.add(session=session, date_for_booking=date_for_booking.date_for_booking, user_id=user.id, times=intervals)

        user.date_for_booking.append(res)

        await session.commit()
        return {"message": "Booking added successfully"}

        

@booking_router.get('/{personal_link}/new')
async def get_booking(
    personal_link: str, date: date, 
    session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications)
    ):

    user_link: User = await UserRepository.find_one_or_none(session=session, personal_link=personal_link)
    if not user_link:
        raise UserNotFound
    booking: Booking = await BookingRepository.get_booking(user_id=user_link.id, session=session, date=date)

