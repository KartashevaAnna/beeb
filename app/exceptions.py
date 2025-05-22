from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


def beeb_exception_handler(request: Request, exc: HTTPException):
    if hasattr(exc, "status_code"):
        return JSONResponse(
            status_code=exc.status_code, content={"message": exc.detail}
        )
    else:
        return JSONResponse(content={"message": str(exc)})


class BeebError(Exception):
    def __init__(self, value: int):
        self.value = value
        self.detail = ""
        self.status_code = None


class ValueTooLargeError(BeebError):
    def __init__(self, value: int):
        self.limit = 999999900
        self.value = value
        self.detail = f"Сумма не может превышать 9999999. Вы ввели: {value}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class NotPositiveValueError(BeebError):
    def __init__(self, value: int):
        self.value = value
        self.detail = f"Сумма должна быть больше нуля. Вы ввели: {value}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class NotIntegerError(BeebError):
    def __init__(self, value):
        self.value = value
        self.detail = f"Сумма должна быть цифрой. Вы ввели: {value}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class DuplicateNameCreateError(BeebError):
    def __init__(self, value: str):
        self.value = value
        self.detail = f"Запись {value} уже существует"
        self.status_code = status.HTTP_406_NOT_ACCEPTABLE


class DuplicateNameEditError(BeebError):
    def __init__(self, value: str):
        self.value = value
        self.detail = f"Запись {value} уже существует"
        self.status_code = status.HTTP_304_NOT_MODIFIED


class UserNotFoundError(BeebError):
    def __init__(self, value: str):
        self.detail = f"Пользователь с именем {value} не найден"
        self.status_code = status.HTTP_404_NOT_FOUND


class WrongPasswordError(BeebError):
    def __init__(self, username: str, password: str):
        first_part_message = f"Пользователя с именем {username} "
        second_part_message = f"и паролем {password} не существует"
        self.detail = first_part_message + second_part_message
        self.status_code = status.HTTP_401_UNAUTHORIZED


class EmptyStringError(BeebError):
    def __init__(self):
        self.detail = "Значение не может быть пустой строкой"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class ExpiredTokenError(BeebError):
    def __init__(self):
        self.detail = "Срок действия токена истёк"
        self.status_code = status.HTTP_401_UNAUTHORIZED


class InvalidTokenError(BeebError):
    def __init__(self):
        self.detail = "Токен не действителен"
        self.status_code = status.HTTP_401_UNAUTHORIZED


class NotOwnerError(BeebError):
    def __init__(self, value):
        self.detail = f"Не вы завели запись {value}"
        self.status_code = status.HTTP_401_UNAUTHORIZED
