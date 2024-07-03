from email.message import EmailMessage

from pydantic import EmailStr

from config import settings


def register_confirmation_template(email_to: EmailStr):
    email = EmailMessage()
    email['Subject'] = 'Регистрация аккаунта'
    email['From'] = settings.SMTP_USER
    email['To'] = email_to

    email.set_content(
        f'''
            <h1>Scheduler</h1>
            <h2>Успешная регистрация на сервисе</h2>
            <h3>Если вы не регистрировались, то проигнорируйте данное сообщение.</h3>
        ''',
        subtype='html',
    )

    return email


def forgot_password_email_template(email_to: EmailStr, token: str):
    email = EmailMessage()
    email["Subject"] = "Сброс пароля"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h2>Вы сделали запрос на сброс пароля</h2>

        <p>Нажмитие на кнопку ниже для сброса вашего пароля</p>
        <br>
        <a style=" padding: 1rem; width: 250px; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;" href="http://127.0.0.1:8000/user/reset/reset_password?token={token}">
            Сбросить пароль
        <a>
        <br>
        <br>
        <p>Если вы ничего не запрашивали, то проигнорируйте данное письмо</p>
    """,
        subtype="html",
    )

    return email


def password_changed_email_template(
    email_to: EmailStr, new_password: str
):
    email = EmailMessage()
    email["Subject"] = "Пароль изменен"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h3>Ваш пароль был сброшен</h3>
        <b><p>Новый пароль: {new_password}</p></b>
        <b><p>Теперь вы можете войти в систему с новым паролем и изменить его если захотите</p></b>
    """,
        subtype="html",
    )

    return email

def success_update_password(
    email_to: EmailStr, new_password: str
):
    email = EmailMessage()
    email["Subject"] = "Пароль изменен"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h3>Вы изменили пароль</h3>
        <b><p>Новый пароль: {new_password}</p></b>
        <b><p>Теперь вы можете войти в систему с новым паролем и изменить его если захотите</p></b>
    """,
        subtype="html",
    )

    return email