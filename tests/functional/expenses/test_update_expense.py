from unittest.mock import patch

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from app.utils.constants import CATEGORIES
from app.utils.tools.helpers import get_readable_price
from tests.conftest import get_categories, raise_always

NAME = "potatoe"
PRICE = 6500
CATEGORY = CATEGORIES[0]


def test_serve_template_update_expense(client, expense, session):
    """Case: endpoint returns form to update an expense."""
    response = client.get(
        SETTINGS.urls.update_expense.format(expense_id=expense.id)
    )
    assert response.status_code == 200
    assert expense.name.title() in response.text
    assert str(expense.id) in response.text
    assert get_readable_price(expense.price) in response.text
    assert expense.expense_category.name in response.text


def test_update_expense_standard_mode_name_lowercase_price_int(
    client, expense, session
):
    """Case: endpoint updates an expense.

    Name is lowercase, price is integer.
    """

    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": PRICE,
            "expense_id": expense.id,
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.expenses
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME
    assert updated_expense.price == PRICE
    assert updated_expense.expense_category == expense.expense_category


def test_update_expense_standard_mode_name_title_price_int(
    client, expense, session
):
    """Case: endpoint updates an expense.

    Name is a title, price is integer.
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME.title(),
            "price": PRICE,
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.expenses
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME


def test_update_expense_standard_mode_name_upper_price_int(
    client, expense, session
):
    """Case: endpoint updates an expense.

    Name is uppercase, price is integer.
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME.upper(),
            "price": PRICE,
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.expenses
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME
    assert (
        updated_expense.expense_category.name == expense.expense_category.name
    )


def test_update_expense_standard_mode_name_lowercase_price_frontend(
    client, expense, session
):
    """Case: endpoint updates an expense.

    Name is lowercase, price is localized string with currency symbol.
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": "65,00₽",
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.expenses
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME
    assert updated_expense.price == PRICE
    assert (
        updated_expense.expense_category.name == expense.expense_category.name
    )


def test_update_expense_name_lowercase_price_int_zero(client, expense, session):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is zero (int).
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": 0,
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_name_lowercase_price_frontend_zero(
    client, expense, session
):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is zero (localized string with currency symbol).
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": "00,00₽",
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_name_lowercase_price_frontend_negative(
    client, expense, session
):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is negative
    (localized string with currency symbol).
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": "-56,00₽",
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_name_lowercase_price_int_negative(client, expense):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is a negative integer.
    """
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": -56,
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_serve_template_404(client):
    """Case: user requests update of a nonexistant expense.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.update_expense.format(expense_id=1))
    assert response.status_code == 404


@patch.object(ExpensesRepo, "update", raise_always)
def test_update_expense_exception(client, expense):
    """Case: any exception is thrown."""
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": 56,
            "category": expense.expense_category.name,
            "form_disabled": True,
        },
    )
    assert response.status_code == 501
    assert "exception" in response.text


def test_update_expense_update_category(client, session, fill_db, expense):
    """Case: endpoint updates an expense with a new category.

    Name is uppercase, price is integer.
    """
    previous_category = expense.expense_category.name
    categories = get_categories(session)
    categories = [x.name for x in categories]
    categories.remove(previous_category)
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": PRICE,
            "category": categories[0],
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.expenses
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME
    assert updated_expense.price == PRICE
    assert updated_expense.expense_category.name != previous_category
