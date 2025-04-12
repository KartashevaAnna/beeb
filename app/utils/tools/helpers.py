import locale
import math
import random

from app.models import Category, Expense
from app.schemas.categories import CategoryCreate
from app.utils.constants import PRODUCTS


def add_expenses_to_db(session, category_id: int) -> Expense:
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
        category_id=category_id,
    )
    session.add(expense)
    session.commit()
    return expense


def add_category_to_db(session, name: str) -> Category:
    category = Category(**CategoryCreate(name=name).__dict__)
    session.add(category)
    session.commit()
    return category


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


def get_expenses_sums_per_category(
    all_expenses: list[Expense],
) -> dict[int, str]:
    expenses_sums_per_category = {}
    for expense in all_expenses:
        if (
            expense.expense_category.name
            not in expenses_sums_per_category.keys()
        ):
            expenses_sums_per_category[expense.expense_category.name] = (
                expense.price
            )
        else:
            expenses_sums_per_category[expense.expense_category.name] = (
                expense.price
                + expenses_sums_per_category[expense.expense_category.name]
            )
    return expenses_sums_per_category


def get_expenses_shares(expenses_per_categories: dict, total: int) -> dict:
    return {
        key: math.floor(expenses_per_categories[key] * 100 / total)
        for key in expenses_per_categories
    }


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
