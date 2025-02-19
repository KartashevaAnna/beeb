import locale
import random

from app.models import Expense
from tests.constants import PRODUCTS


def add_expenses_to_db(session) -> Expense:
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
    )
    session.add(expense)
    session.commit()


def get_readable_price(price: int) -> str:
    """Formats price as per Russian locale and appends currency symbol."""
    return (
        locale.format_string("%.2f", (price / 100), grouping=True)
        + locale.localeconv()["currency_symbol"]
    )


def get_number_for_db(frontend_input: str) -> int:
    """Removes price format as per Russian locale, returns price in kopecks."""
    currency_symbol = locale.localeconv()["currency_symbol"]
    removed_currency_symbol = frontend_input.replace(currency_symbol, "")
    removed_decimal = removed_currency_symbol.replace(",", "")
    return locale.atoi(removed_decimal)
