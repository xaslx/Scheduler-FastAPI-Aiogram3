import smtplib
from time import sleep

from pydantic import EmailStr

from app.tasks.celery_app import celery
from app.tasks.email_templates import (add_new_client, cancel_booking,
                                       confirm_booking,
                                       forgot_password_email_template,
                                       get_help,
                                       password_changed_email_template,
                                       register_confirmation_template,
                                       send_notification_for_all_users,
                                       success_update_password,
                                       cancel_booking_for_me)
from config import settings
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


bot: Bot = Bot(settings.TOKEN_BOT, default=DefaultBotProperties(parse_mode="HTML"))


async def cancel_booking_tg_client(user_id: int, date: str, time: str, description: str):
    await bot.send_message(
        chat_id=user_id, 
        text=
        f'<b>Вашу запись отменили</b>\n\n'
        f'Дата: <b>{date}</b>\n'
        f'Время: <b>{time}</b>\n'
        f'Причина: <b>{description}</b>',
    )

async def cancel_booking_tg_owner(owner_id: int, name: str, email: EmailStr, phone_number: str, date: str, time: str, description: str):
    await bot.send_message(
        chat_id=owner_id, 
        text=
        f'<b>Вы отменили запись пользователю</b>\n\n'
        f'Инфо о клиенте:\n'
        f'Имя: <b>{name}</b>\n'
        f'Email: <b>{email}</b>\n'
        f'Телефона: <b>{phone_number}</b>\n\n'
        f'Инфо о времени и причина:\n'
        f'Дата: <b>{date}</b>\n'
        f'Время: <b>{time}</b>\n'
        f'Причина: <b>{description}</b>',
    )

async def new_client_tg(user_id: int, date: str, time: str, name: str, phone_number: str, user_email: EmailStr):
    await bot.send_message(
        chat_id=user_id,
        text=
        f'К вам записался новый клиент!\n'
        f'Дата: <b>{date}</b>\n'
        f'Время: <b>{time}</b>\n\n'
        f'<b>Информация о клиенте</b>\n'
        f'Имя: <b>{name}</b>\n'
        f'Телефон: <b>{phone_number}</b>\n'
        f'Email клиента: <b>{user_email}</b>\n'
    )

async def new_booking_tg(user_id: int, date: str, time: str, email: EmailStr):
    await bot.send_message(
        chat_id=user_id,
        text=
        f'Вы успешно записались\n'
        f'Дата: <b>{date}</b>\n'
        f'Время: <b>{time}</b>\n\n'
        f'<b>Если хотите отменить запись то напишите на почту</b>\n'
        f'Email: <b>{email}</b>\n'
        f'Или же отменить в телеграм /bookings'
    )



@celery.task
def register_confirmation_message(email_to: EmailStr):
    msg_content = register_confirmation_template(email_to=email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def reset_password_email(email: EmailStr, token: str):
    msg_content = forgot_password_email_template(email, token)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def password_changed(email: EmailStr, new_password: str):

    msg_content = password_changed_email_template(email, new_password)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def update_password(email: EmailStr, new_password: str):

    msg_content = success_update_password(email_to=email, new_password=new_password)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def new_client(email: EmailStr, date: str, time: str, name: str, phone_number: str, user_email: EmailStr, tg: str):
    msg_content = add_new_client(email_to=email, date=date, time=time, name=name, phone_number=phone_number, user_email=user_email, tg=tg)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def cancel_client(
    email: EmailStr, date: str, time: str, description: str
):
    msg_content = cancel_booking(
        email_to=email, date=date, time=time, description=description
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def cancel_client_for_me(
    email_to: EmailStr, name: str, email: EmailStr, phone_number: str, date: str, time: str, description: str 
):
    msg_content = cancel_booking_for_me(
        email_to=email_to, name=name, email_user=email, phone_number=phone_number, date=date, time=time, description=description
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def send_notification(users: list, message: str):

    for user in users:
        msg_content = send_notification_for_all_users(user, message)

        sleep(1)
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)


@celery.task
def help_message(email: EmailStr, description: str):
    msg_content = get_help(email_from=email, description=description)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery.task
def confirm_booking_for_client(
    email_to: EmailStr, tg: str, em: EmailStr, time: str, date: str
):
    msg_content = confirm_booking(email_to=email_to, tg=tg, em=em, time=time, date=date)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
