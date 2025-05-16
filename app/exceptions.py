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


class DuplicateEmailError(BeebError):
    def __init__(self, value: int):
        self.value = value
        self.detail = f"Пользователь с email {value} уже существует"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
