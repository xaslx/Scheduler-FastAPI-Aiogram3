from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib3 import HTTPResponse

from app.auth.dependencies import get_all_notifications, get_current_user
from app.models.booking_model import Booking
from app.models.user_model import User
from app.repository.booking_repo import BookingRepository
from app.repository.user_repo import UserRepository
from app.schemas.booking_schemas import (BookingDate, BookingOut, CancelBooking,
                                         CreateBooking)
from app.schemas.notification_schemas import NotificationOut
from app.schemas.user_schema import UserOut
from app.tasks.tasks import (cancel_client, confirm_booking_for_client,
                             new_client, cancel_client_for_me, cancel_booking_tg_client, cancel_booking_tg_owner,
                             new_booking_tg, new_client_tg)
from app.utils.generate_time import generate_time_intervals
from app.utils.templating import templates
from database import get_async_session
from exceptions import BookingNotFound, NotAccessError, UserNotFound
from logger import logger
from app.utils.generate_time import moscow_tz


booking_router: APIRouter = APIRouter(prefix="/booking", tags=["Запись"])


@booking_router.get("/{personal_link}", status_code=200, name="personal_link:page")
async def get_booking_by_link(
    personal_link: Annotated[str, Path()],
    request: Request,
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    user_link: UserOut = await UserRepository.find_one_or_none(
        session=session, personal_link=personal_link
    )
    if user_link is None:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )
    template: HTMLResponse = templates.TemplateResponse(
        request=request,
        name="booking.html",
        context={"user": user, "user_link": user_link, "notifications": notifications},
    )
    logger.info(f'Открытие персональной ссылки у пользователя: ID={user_link.id}')
    return template

@booking_router.post("/add_booking", status_code=201)
async def add_booking(
    date_for_booking: BookingDate, session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    user: UserOut = await UserRepository.find_one_or_none(
        session=session, id=date_for_booking.user_id
    )
    date_for: date = date_for_booking.date_for_booking.date() + timedelta(days=1)

    if not user:
        raise UserNotFound
    intervals: list[str] = await generate_time_intervals(
        user.start_time, user.end_time, user.interval
    )

    booking: BookingOut = await BookingRepository.get_booking(
        session=session, user_id=date_for_booking.user_id, date=date_for
    )
    booking_id: int = booking.id if booking else 0

    if not booking:
        booking_id: BookingOut = await BookingRepository.add(
            session=session, date_for_booking=date_for, user_id=user.id, times=intervals
        )
        logger.info(f'Добавление новой даты для пользователя: {user.id}, Дата - {date_for}, Время: {intervals}')

    redirect_url: str = (
        booking_router.url_path_for("gettime:page", personal_link=user.personal_link)
        + f"?date={date_for}&user_id={user.id}&booking_id={booking_id}"
    )
    return JSONResponse(content={"redirect_url": redirect_url}, status_code=200)


@booking_router.get(
    "/{personal_link}/select_time", status_code=200, name="gettime:page"
)
async def get_time(
    personal_link: Annotated[str, Path()],
    booking_id: Annotated[int, Query()],
    date: Annotated[date, Query()],
    user_id: Annotated[int, Query()],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: UserOut = Depends(get_current_user),
    notifications: list[NotificationOut] = Depends(get_all_notifications),
) -> HTMLResponse:
    user_link: UserOut = await UserRepository.find_one_or_none(
        session=session, personal_link=personal_link
    )

    if not user_link.enabled:
        return templates.TemplateResponse(
            request=request,
            name="offbooking.html",
            context={"user": user, "notifications": notifications},
        )

    if (
        not user_link
        or user_link.id != user_id
        or user_link.personal_link != personal_link
    ):
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )

    booking: BookingOut = await BookingRepository.get_booking(
        user_id=user_link.id, date=date, session=session
    )

    if not booking or (booking.id != booking_id):
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"user": user, "notifications": notifications},
        )

    now: datetime = datetime.now(tz=moscow_tz)
    current_time: str = now.strftime("%H:%M")
    current_date = now.date()

    if booking.date_for_booking == current_date:
        available_times = [time for time in booking.times if time > current_time]
    else:
        available_times = booking.times

    template: HTTPResponse = templates.TemplateResponse(
        request=request,
        name="select_time.html",
        context={
            "booking": booking,
            "user_link": user_link,
            "user": user,
            "notifications": notifications,
            "selected_times": booking.selected_times,
            "times": available_times,
            "booking_id": booking_id,
        },
    )
    logger.info(f'Получение свободного времени на дату: {date}, у пользователя: ID={user_link.id}')
    return template


@booking_router.patch("/select_booking/{booking_id}", status_code=200)
async def select_booking(
    booking_id: Annotated[int, Path()],
    bg_task: BackgroundTasks,
    create_booking: CreateBooking,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    booking: BookingOut = await BookingRepository.find_one_or_none(
        session=session, id=booking_id
    )
    user_email: UserOut = await UserRepository.find_one_or_none(
        session=session, id=booking.user_id
    )
    if not user_email or not user_email.is_active:
        raise NotAccessError
    if not booking:
        raise BookingNotFound
    await BookingRepository.select_times(
        session=session,
        user_id=booking.user_id,
        booking_id=booking.id,
        time=(
            create_booking.time,
            create_booking.name,
            create_booking.phone_number,
            create_booking.email,
            create_booking.tg,
        ),
    )
    logger.info(f'Пользователь: {(create_booking.name,
            create_booking.phone_number,
            create_booking.email)} записался к ID={user_email.id}, date={booking.date_for_booking}, time={create_booking.time}')
    # confirm_booking_for_client.delay(
    #     email_to=create_booking.email,
    #     tg=user_email.telegram_link if user_email.telegram_link else "Не указан",
    #     em=user_email.email,
    #     time=create_booking.time,
    #     date=str(booking.date_for_booking),
    # ) Celery
    bg_task.add_task(
        confirm_booking_for_client,
        email_to=create_booking.email,
        tg=user_email.telegram_link if user_email.telegram_link else "Не указан",
        em=user_email.email,
        time=create_booking.time,
        date=str(booking.date_for_booking)
    )
    logger.info(f'Пользователю: {(create_booking.name,
            create_booking.phone_number,
            create_booking.email)} отправлено письмо о успешной записи')
    # new_client.delay(
    #     email=user_email.email,
    #     date=str(booking.date_for_booking),
    #     time=create_booking.time,
    #     name=create_booking.name,
    #     phone_number=create_booking.phone_number,
    #     user_email=create_booking.email,
    #     tg=create_booking.tg if create_booking.tg else 'Не указан',
    # ) Celery
    bg_task.add_task(
        new_client, 
        email=user_email.email,
        date=str(booking.date_for_booking),
        time=create_booking.time,
        name=create_booking.name,
        phone_number=create_booking.phone_number,
        user_email=create_booking.email,
        tg=create_booking.tg if create_booking.tg else 'Не указан'
    )
    logger.info(f'Пользователю: {(user_email.email, user_email.name, user_email.surname, user_email.id)} отправлено письмо о новом клиенте')
    if create_booking.tg:
        bg_task.add_task(
            new_booking_tg,
            user_id=create_booking.tg,
            date=str(booking.date_for_booking), 
            time=create_booking.time, 
            email=user_email.email
        )
    if user_email.telegram_id:
        bg_task.add_task(
            new_client_tg,
            user_id=user_email.telegram_id,
            date=str(booking.date_for_booking), 
            time=create_booking.time, 
            name=create_booking.name, 
            phone_number=create_booking.phone_number, 
            user_email=create_booking.email,
        )


@booking_router.patch("/cancel_booking", status_code=200)
async def cancel_booking(
    cancel_data: CancelBooking,
    bg_task: BackgroundTasks,
    booking_id: Annotated[int, Query()],
    user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    booking: Booking = await BookingRepository.find_one_or_none(
        session=session, id=booking_id
    )
    if not booking or (booking.user_id != user.id) or not user:
        raise NotAccessError
    await BookingRepository.cancel_times(
        session=session,
        user_id=booking.user_id,
        booking_id=booking.id,
        time=cancel_data.time,
    )
    logger.info(f'Пользователь ID={user.id} отменил запись для клиента:\n \
                email={cancel_data.email}\n \
                time={cancel_data.time}\n \
                date={cancel_data.date}\n \
                Причина={cancel_data.description}')
    # cancel_client.delay(
    #     message="Вам отменили запись.",
    #     email=cancel_data.email,
    #     date=cancel_data.date,
    #     time=cancel_data.time,
    #     description=cancel_data.description,
    # ) Celery
    bg_task.add_task(
        cancel_client,
        email=cancel_data.email,
        date=cancel_data.date,
        time=cancel_data.time,
        description=cancel_data.description 
    )
    logger.info(f'Пользователю {cancel_data.email} отправлено письмо на почту о его отмененной записи')
    # cancel_client.delay(
    #     message=f"Вы отменили запись клиенту.\n{cancel_data.email}",
    #     email=user.email,
    #     date=cancel_data.date,
    #     time=cancel_data.time,
    #     description=cancel_data.description,
    # ) Celery
    bg_task.add_task(
        cancel_client_for_me,
        email_to=user.email,
        name=cancel_data.name,
        email=cancel_data.email,
        phone_number=cancel_data.phone_number,
        date=cancel_data.date,
        time=cancel_data.time,
        description=cancel_data.description,   
    )
    logger.info(f'Пользователю ID={user.id} отправлено письмо на почту об успешной отмене записи')
    if user.telegram_id:
        bg_task.add_task(
            cancel_booking_tg_owner,
            owner_id=user.telegram_id,
            name=cancel_data.name,
            email=cancel_data.email,
            phone_number=cancel_data.phone_number,
            date=cancel_data.date,
            time=cancel_data.time,
            description=cancel_data.description
        )
    if cancel_data.tg_id:
        bg_task.add_task(
            cancel_booking_tg_client,
            int(cancel_data.tg_id),
            date=cancel_data.date,
            time=cancel_data.time,
            description=cancel_data.description
        )
