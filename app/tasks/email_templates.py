from email.message import EmailMessage

from pydantic import EmailStr

from config import settings



def reminder_template(email_to: EmailStr, time: str):
    email = EmailMessage()
    email["Subject"] = "Напоминание"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(f'У вас имеется запись на сегодня<br><b>Время: {time}</b><br>Время указано по <b>Москве</b>', subtype="html")

    return email




def disconnect_tg_template(email_to: EmailStr):
    email = EmailMessage()
    email["Subject"] = "Отключение аккаунта Телеграм"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .outer-container {
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }
                .inner-container {
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }
                h1 {
                    color: #333333;
                }
                h3 {
                    color: #777777;
                }
                .footer {
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }
                .footer a {
                    color: #007bff;
                    text-decoration: none;
                }
                .footer a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Scheduler</h1>
                    <h3>Вы отвязали свой Telegram от сайта.</h3>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def register_confirmation_template(email_to: EmailStr):
    email = EmailMessage()
    email["Subject"] = "Регистрация аккаунта"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .outer-container {
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }
                .inner-container {
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }
                h1 {
                    color: #333333;
                }
                h2 {
                    color: #555555;
                }
                h3 {
                    color: #777777;
                }
                .footer {
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }
                .footer a {
                    color: #007bff;
                    text-decoration: none;
                }
                .footer a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Scheduler</h1>
                    <h2>Успешная регистрация на сервисе</h2>
                    <h3>Если вы не регистрировались, то проигнорируйте данное сообщение.</h3>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email



def forgot_password_email_template(email_to: EmailStr, token: str):
    email = EmailMessage()
    email["Subject"] = "Сброс пароля"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    font-size: 16px;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: #333333;
                }}
                h2 {{
                    color: #555555;
                }}
                h3 {{
                    color: #777777;
                }}
                .button {{
                    padding: 1rem;
                    width: 250px;
                    border-radius: 0.5rem;
                    font-size: 1rem;
                    text-decoration: none;
                    background: #0275d8;
                    color: white;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h2>Вы сделали запрос на сброс пароля</h2>
                    <p>Нажмите на кнопку ниже для сброса вашего пароля</p>
                    <a style="color: white;" class="button" href="https://scheduler-bgly.onrender.com/user/reset/reset_password?token={token}">
                        Сбросить пароль
                    </a>
                    <p>Если вы ничего не запрашивали, то проигнорируйте данное письмо</p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def password_changed_email_template(email_to: EmailStr, new_password: str):
    email = EmailMessage()
    email["Subject"] = "Пароль изменен"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: #333333;
                }}
                h2 {{
                    color: #555555;
                }}
                h3 {{
                    color: #777777;
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h3>Ваш пароль был сброшен</h3>
                    <p><b>Новый пароль: {new_password}</b></p>
                    <p>Теперь вы можете войти в систему с новым паролем и изменить его если захотите</p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def success_update_password(email_to: EmailStr, new_password: str):
    email = EmailMessage()
    email["Subject"] = "Пароль изменен"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: #333333;
                }}
                h2 {{
                    color: #555555;
                }}
                h3 {{
                    color: #777777;
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h3>Вы изменили пароль</h3>
                    <p><b>Новый пароль: {new_password}</b></p>
                    <p>Теперь вы можете войти в систему с новым паролем и изменить его, если захотите.</p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def add_new_client(email_to: EmailStr, date: str, time: str, name: str, phone_number: str, user_email: EmailStr, tg: str):
    email = EmailMessage()
    email["Subject"] = "Новая запись!"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: #333333;
                }}
                h2 {{
                    color: #555555;
                }}
                h3 {{
                    color: #777777;
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>К вам записался новый клиент!</h1>
                    <p>Дата: <b>{date}</b></p>
                    <p>Время: <b>{time}</b></p>
                    </br>
                    </br>
                    <p><b><i>Информация о клиенте</i></b></p>
                    <p>Имя: <b>{name}</b></p>
                    <p>Телефон: <b>{phone_number}</b></p>
                    <p>Email клиента: <b>{user_email}</b></p>
                    <p>Telegram: <b>{tg}</b></p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def cancel_booking(
    email_to: EmailStr, date: str, time: str, description: str
):
    email = EmailMessage()
    email["Subject"] = "Отмена записи!"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: #d9534f; /* Цвет для важного сообщения */
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Вам отменили запись</h1>
                    <p>Дата: <b>{date}</b></p>
                    <p>Время: <b>{time}</b> (МСК)</p>
                    <p>Причина: <b>{description}</b></p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email

def cancel_booking_for_me(
    email_to: EmailStr, name: str, email_user: EmailStr, phone_number: str, date: str, time: str, description: str
):
    email = EmailMessage()
    email["Subject"] = "Отмена записи!"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: #d9534f; /* Цвет для важного сообщения */
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Вы отменили запись клиенту:</h1>
                    <br>
                    <b>Имя: {name}</b><br>
                    <b>Email: {email_user}</b><br>
                    <b>Телефон: {phone_number}<b></br>
                    <p>Дата: <b>{date}</b></p>
                    <p>Время: <b>{time}</b> (МСК)</p>
                    <p>Причина: <b>{description}</b></p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def confirm_booking(email_to: EmailStr, tg: str, em: EmailStr, time: str, date: str):
    email = EmailMessage()
    email["Subject"] = "Успешная запись"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h1 {{
                    color: green;
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                b {{
                    color: #333333;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Вы сделали запись</h1>
                    <p>Время: <b>{time}</b> (МСК) </p>
                    <p>Дата: <b>{date}</b></p>
                    <p><b>Если вы хотите отменить запись, свяжитесь с нами:</b></p>
                    <p>По Email: <b>{em}</b></p>
                    <p>Или Telegram: <b>{tg}</b></p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def send_notification_for_all_users(email_to: EmailStr, message: str):
    email = EmailMessage()
    email["Subject"] = "Рассылка уведомления"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                h1 {{
                    color: #0275d8; /* Цвет для заголовка уведомления */
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Уведомление</h1>
                    <p>{message}</p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email


def get_help(email_from: EmailStr, description: str):
    email = EmailMessage()
    email["Subject"] = "Помощь"
    email["From"] = settings.SMTP_USER
    email["To"] = settings.SMTP_USER

    email.set_content(
        f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .outer-container {{
                    background-color: #e0e0e0;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 600px;
                    margin: auto;
                }}
                .inner-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                    line-height: 1.6;
                }}
                h1 {{
                    color: #d9534f; /* Цвет для заголовка запроса помощи */
                }}
                p {{
                    color: #555555;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555555;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="outer-container">
                <div class="inner-container">
                    <h1>Запрос на помощь</h1>
                    <p><strong>Email:</strong> {email_from}</p>
                    <p><i>Описание проблемы:</i></p>
                    <p><b>{description}</b></p>
                </div>
                <div class="footer">
                    <a href="https://t.me/xaslx">Telegram если возникли трудности с сервисом.</a>
                </div>
            </div>
        </body>
        </html>
        """,
        subtype="html"
    )

    return email
