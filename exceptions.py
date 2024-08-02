from fastapi import HTTPException, status


class BaseException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


# Пользователи
class UserAlreadyExistsException(BaseException):
    status_code = 409
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BaseException):
    status_code = 401
    detail = "Неверный email или пароль"


class IncorrectEmailOrPasswordExceptionNotEn(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Email или пароль должны быть на английском"


class UserNotFound(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь не найден"


class NotAccessError(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Недостаточно прав"


class UserIsNotPresentException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED


class UserIsNotAdmin(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Доступ запрещен"


class UserAlreadyUnBan(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже разблокирован"


class IncorrectNameOrSurnameException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Некоректное имя или фамилия"


class UserAlreadyBan(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже заблокирован"


class UnverifiedUser(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Вы не верифицированный пользователь"

class BookingError(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не удалось сделать запись"

class YourAccountIsBlocked(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Ваш аккаунт заблокирован"


class FileTooLarge(BaseException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    detail = "Файл не должен привышать 5мб."


class NotificationNotFound(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Уведомление не найден"


# JWT token
class TokenExpiredException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истёк"


class TokenAbsentException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class BookingNotFound(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Запись не найдена"


class TimeNotFound(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Время для записи не найдено"
