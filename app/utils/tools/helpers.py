import locale
import random

from app.models import Expense
from app.utils.constants import PRODUCTS
from app.utils.enums import ExpenseCategory


def add_expenses_to_db(session) -> Expense:
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
        category=random.choice(ExpenseCategory.list_names()),
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


def get_expenses_options(current_option: str) -> list:
    """Gets all expenses options.

    Sorts options so that the one currently selected is on top.
    """
    all_options = ExpenseCategory.list_names()
    sorted_options = [current_option]
    all_options.remove(current_option)
    all_options = sorted(all_options)
    sorted_options.extend(iter(all_options))
    return sorted_options


def get_monthly_expenses(all_expenses: list[Expense]) -> dict[int, str]:
    monthly_expenses = {}
    for expense in all_expenses:
        if expense.created_at.strftime("%m") not in monthly_expenses.keys():
            monthly_expenses[expense.created_at.strftime("%m")] = expense.price
        else:
            monthly_expenses[expense.created_at.strftime("%m")] = (
                expense.price
                + monthly_expenses[expense.created_at.strftime("%m")]
            )
    return monthly_expenses
