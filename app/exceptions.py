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
        self.message = ""
        self.status_code = None
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class ValueTooLargeError(BeebError):
    def __init__(self, value: int):
        self.limit = 999999900
        self.value = value
        self.message = f"Сумма не может превышать 9999999. Вы ввели: {value}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class NotPositiveValueError(BeebError):
    def __init__(self, value: int):
        self.value = value
        self.message = f"Сумма должна быть больше нуля. Вы ввели: {value}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class NotIntegerError(BeebError):
    def __init__(self, value):
        self.value = value
        self.message = f"Сумма должна быть цифрой. Вы ввели: {value}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class DuplicateNameCreateError(BeebError):
    def __init__(self, value: str):
        self.value = value
        self.message = f"Запись {value} уже существует"
        self.status_code = status.HTTP_406_NOT_ACCEPTABLE
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class DuplicateNameEditError(BeebError):
    def __init__(self, value: str):
        self.value = value
        self.message = f"Запись {value} уже существует"
        self.status_code = status.HTTP_304_NOT_MODIFIED
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class UserNotFoundError(BeebError):
    def __init__(self, value: str):
        self.message = f"Пользователь с именем {value} не найден"
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class WrongPasswordError(BeebError):
    def __init__(self, username: str, password: str):
        first_part_message = f"Пользователя с именем {username} "
        second_part_message = f"и паролем {password} не существует"
        self.message = first_part_message + second_part_message
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class EmptyStringError(BeebError):
    def __init__(self):
        self.message = "Значение не может быть пустой строкой"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class ExpiredTokenError(BeebError):
    def __init__(self):
        self.message = "Срок действия токена истёк"
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class InvalidTokenError(BeebError):
    def __init__(self):
        self.message = "Токен не действителен"
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class NotOwnerError(BeebError):
    def __init__(self, value):
        self.message = f"Не вы завели запись {value}"
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class NothingToComputeError(BeebError):
    def __init__(self):
        self.message = "Недостаточно данных для расчётов"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class SpendingOverBalanceError(BeebError):
    def __init__(self, spending, balance):
        self.value = spending
        self.balance = balance
        self.message = f"Расход {spending // 100} превышает сумму, которая есть на счету: {balance // 100}."
        self.status_code = status.HTTP_406_NOT_ACCEPTABLE
        self.detail = f"Код ошибки: {self.status_code}. " + self.message


class IncomeNotFoundError(BeebError):
    def __init__(
        self,
        value: str,
    ):
        self.message = f"Доход под номером {value} не найден"
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"Код ошибки: {self.status_code}. " + self.message
