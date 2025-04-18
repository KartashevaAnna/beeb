import datetime
import locale
import random

from app.models import Payment
from app.utils.constants import PRODUCTS


def add_payments_to_db(session, category_id: int) -> Payment:
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
        category_id=category_id,
    )
    session.add(payment)
    session.commit()
    return payment


def convert_to_copecks(price: int) -> int:
    return price * 100


def convert_to_rub(price: int) -> int:
    return price / 100


def get_readable_price(price: int) -> str:
    """Formats price as per Russian locale and appends currency symbol."""
    return (
        locale.format_string("%.0f", (convert_to_rub(price)), grouping=True)
        + locale.localeconv()["currency_symbol"]
    )


def get_number_for_db(frontend_input: str) -> int:
    """Removes price format as per Russian locale, returns price in kopecks."""
    currency_symbol = locale.localeconv()["currency_symbol"]
    if frontend_input:
        removed_currency_symbol = frontend_input.replace(currency_symbol, "")
        return convert_to_copecks(locale.atoi(removed_currency_symbol))


def get_monthly_payments(all_payments: list[Payment]) -> dict[int, str]:
    monthly_payments = {}
    for payment in all_payments:
        if payment.created_at.strftime("%m") not in monthly_payments.keys():
            monthly_payments[payment.created_at.strftime("%m")] = payment.price
        else:
            monthly_payments[payment.created_at.strftime("%m")] = (
                payment.price
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


def get_date_from_datetime(date: datetime.datetime) -> str:
    return f"{date.strftime('%d %B %Y')} года"


def get_date_from_datetime_without_year(date: datetime.datetime) -> str:
    return date.strftime("%d %B")


def get_datetime_from_date(date: str) -> datetime.datetime:
    date = date[:-5]
    date_str = f"{date} 00:00:00.000001"
    date = datetime.datetime.strptime(date_str, "%d %B %Y %H:%M:%S.%f")
    return date.astimezone()
