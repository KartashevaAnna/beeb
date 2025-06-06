import datetime
import locale
import random
import re
from hashlib import sha256
from calendar import isleap
from app.exceptions import (
    BeebError,
    EmptyStringError,
    NotIntegerError,
    NotPositiveValueError,
    ValueTooLargeError,
)
from app.models import Payment
from app.settings import SETTINGS
from app.utils.constants import INT_TO_MONTHS, PRODUCTS


def add_payments_to_db(session, category_id: int, user_id: int) -> Payment:
    payment = Payment(
        user_id=user_id,
        name=random.choice(PRODUCTS),
        amount=random.randrange(100, 5000, 100),
        category_id=category_id,
    )
    session.add(payment)
    session.commit()
    return payment


def convert_to_copecks(amount: int) -> int:
    return amount * 100


def convert_to_rub(amount: int) -> int:
    return amount // 100


def get_readable_number(amount: int) -> str:
    """Formats amount as per Russian locale"""
    return locale.format_string("%.0f", amount, grouping=True)


def get_readable_amount(amount: int) -> str:
    """Formats amount as per Russian locale and appends currency symbol."""
    return (
        locale.format_string(
            "%.0f", (convert_to_rub(amount)), grouping=True, monetary=True
        )
        + " "
        + locale.localeconv()["currency_symbol"]
    )


def get_number_for_db(frontend_input: str) -> int:
    """Removes amount format as per Russian locale, returns amount in kopecks."""
    currency_symbol = locale.localeconv()["currency_symbol"]
    removed_currency_symbol = frontend_input.replace(currency_symbol, "")
    return convert_to_copecks(locale.atoi(removed_currency_symbol))


def get_monthly_payments(all_payments: list[Payment]) -> dict[int, str]:
    monthly_payments = {}
    for payment in all_payments:
        if payment.created_at.strftime("%m") not in monthly_payments.keys():
            monthly_payments[payment.created_at.strftime("%m")] = payment.amount
        else:
            monthly_payments[payment.created_at.strftime("%m")] = (
                payment.amount
                + monthly_payments[payment.created_at.strftime("%m")]
            )
    return monthly_payments


def sort_options(
    all_options: list[str], current_option: str | None = None
) -> list:
    """Gets all options.

    Sorts options so that:
    - the one currently selected is on top
    - if nothing is selected, first created item shall always be on top
    """
    first_option = all_options[0]
    all_options.remove(first_option)
    if current_option not in all_options:
        sorted_options = []
    else:
        sorted_options = [current_option]
        all_options.remove(current_option)
    all_options = sorted(all_options)
    sorted_options.append((first_option))
    sorted_options.extend(iter(all_options))
    return sorted_options


def has_cyrillic(date: str):
    return bool(re.search("[а-яА-Я]", date))


def get_date_from_datetime(date: datetime.datetime) -> str:
    return f"{date.strftime('%d %B %Y')} года"


def get_pure_date_from_datetime(date: datetime.datetime) -> str:
    return date.strftime("%d.%m.%Y")


def get_datetime_without_seconds(date: datetime.datetime) -> str:
    return f"{date.strftime('%Y-%m-%d %X')}"


def get_date_from_datetime_without_year(date: datetime.datetime) -> str:
    return date.strftime("%d %B")


def get_datetime_from_date(date: str) -> datetime.datetime:
    date = date[:-5]
    date_str = f"{date} 00:00:00.000001"
    date = datetime.datetime.strptime(date_str, "%d %B %Y %H:%M:%S.%f")
    return date.astimezone()


def get_datetime_from_time_string(date) -> str:
    now = datetime.datetime.now()
    now_time = str(now)[10:]
    date = f"{date}{now_time}"
    res = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S.%f")
    return res.astimezone()


def get_date_for_database(date) -> str:
    if has_cyrillic(date):
        return get_datetime_from_date(date)
    return get_datetime_from_time_string(date)


def hash_password(password: str) -> bytes:
    password_encrypted = sha256(
        (f"{SETTINGS.secrets.salt}{password}").encode("utf-8")
    ).hexdigest()
    return str.encode(password_encrypted)


def is_same_password(password: str, password_hash_sum: bytes) -> bool:
    return hash_password(password) == password_hash_sum


def prevent_blank_strings(value):
    for _ in range(len(value)):
        value = value.replace("  ", " ")
    if value.isspace():
        raise EmptyStringError
    if not value:
        raise EmptyStringError
    return value


def get_current_year_and_month() -> list:
    now = datetime.datetime.now()
    return [now.year, now.month]


def check_current_year_and_month(year: int, month: int) -> list:
    current_year, current_month = get_current_year_and_month()
    return current_year == year and INT_TO_MONTHS[current_month] == month


def validate_positive_number_for_db(
    value: int | None = None,
) -> int | BeebError:
    if value is None:
        return value
    try:
        value = int(value)
    except ValueError:
        raise NotIntegerError(value)
    if value <= 0:
        raise NotPositiveValueError(value)
    if value > 9999999:
        raise ValueTooLargeError(value)
    return value


def get_max_days_in_month(month: int, year: int) -> int:
    days_in_month = {
        "январь": 31,
        "февраль": 29 if isleap(year) else 28,
        "март": 31,
        "апрель": 30,
        "май": 31,
        "июнь": 30,
        "июль": 31,
        "август": 31,
        "сентябрь": 30,
        "октябрь": 31,
        "ноябрь": 30,
        "декабрь": 31,
    }
    return days_in_month[INT_TO_MONTHS[month]]


def get_max_date_from_year_and_month(
    year: int, month: int
) -> datetime.datetime:
    time = "23:59:59.999999"
    day = get_max_days_in_month(year=year, month=month)
    return f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)} {time}"


def get_max_date_from_year_and_month_datetime_format(
    year: int, month: int
) -> datetime.datetime:
    time = "23:59:59.999999"
    day = get_max_days_in_month(year=year, month=month)
    date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)} {time}"
    res = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    return res.astimezone()


def get_min_date_from_year_and_month_datetime_format(
    year: int, month: int
) -> datetime.datetime:
    time = "00:00:00.000001"
    day = 1
    date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)} {time}"
    res = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    return res.astimezone()
