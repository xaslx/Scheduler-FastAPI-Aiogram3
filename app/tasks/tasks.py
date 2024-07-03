import smtplib

from pydantic import EmailStr

from config import settings
from app.tasks.celery_app import celery
from app.tasks.email_templates import send_notification_for_all_users, register_confirmation_template, forgot_password_email_template, password_changed_email_template, success_update_password


@celery.task
def register_confirmation_message(email_to: EmailStr):
    msg_content = register_confirmation_template(email_to=email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)

@celery.task
def reset_password_email(email: EmailStr, token: str):
    msg_content = forgot_password_email_template(email, token)

    with smtplib.SMTP_SSL(
            settings.SMTP_HOST, settings.SMTP_PORT
        ) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)

@celery.task
def password_changed(email: EmailStr, new_password: str):

    msg_content = password_changed_email_template(email, new_password)

    with smtplib.SMTP_SSL(
            settings.SMTP_HOST, settings.SMTP_PORT
        ) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)

@celery.task
def update_password(email: EmailStr, new_password: str):

    msg_content = success_update_password(email_to=email, new_password=new_password)

    with smtplib.SMTP_SSL(
            settings.SMTP_HOST, settings.SMTP_PORT
        ) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)


@celery.task
def send_notification(users: list, message: str):

    for user in users:
        msg_content = send_notification_for_all_users(user, message)

        with smtplib.SMTP_SSL(
            settings.SMTP_HOST, settings.SMTP_PORT
        ) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)