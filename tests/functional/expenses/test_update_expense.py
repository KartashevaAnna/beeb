from unittest.mock import patch

from sqlalchemy import select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_readable_price
from tests.functional.conftest import fill_db, raise_always

NAME = "potatoe"
PRICE = 6500


def test_serve_template_update_expense(client, fill_db, session):
    """Case: endpoint returns form to update an expense."""
    expense = session.scalars(select(Expense)).first()
    response = client.get(
        SETTINGS.urls.update_expense.format(expense_id=expense.id)
    )
    assert response.status_code == 200
    assert expense.name.title() in response.text
    assert str(expense.id) in response.text
    assert get_readable_price(expense.price) in response.text


def test_update_expense_standard_mode_name_lowercase_price_int(
    client, fill_db, session
):
    """Case: endpoint updates an expense.

    Name is lowercase, price is integer.
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": PRICE,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME
    assert updated_expense.price == PRICE


def test_update_expense_standard_mode_name_title_price_int(
    client, fill_db, session
):
    """Case: endpoint updates an expense.

    Name is a title, price is integer.
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME.title(),
            "price": PRICE,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME


def test_update_expense_standard_mode_name_upper_price_int(
    client, fill_db, session
):
    """Case: endpoint updates an expense.

    Name is uppercase, price is integer.
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME.upper(),
            "price": PRICE,
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME


def test_update_expense_standard_mode_name_lowercase_price_frontend(
    client, fill_db, session
):
    """Case: endpoint updates an expense.

    Name is lowercase, price is localized string with currency symbol.
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": "65,00₽",
            "form_disabled": True,
        },
    )
    assert response.status_code == 303
    session.expire_all()
    updated_expense = session.get(Expense, expense.id)
    assert expense.id == updated_expense.id
    assert updated_expense.name == NAME
    assert updated_expense.price == PRICE


def test_update_expense_name_lowercase_price_int_zero(client, fill_db, session):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is zero (int).
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": 0,
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_name_lowercase_price_frontend_zero(
    client, fill_db, session
):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is zero (localized string with currency symbol).
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": "00,00₽",
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_name_lowercase_price_frontend_negative(
    client, fill_db, session
):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is negative
    (localized string with currency symbol).
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": "-56,00₽",
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_name_lowercase_price_int_negative(
    client, fill_db, session
):
    """Case: endpoint fails updating an expense.

    Name is lowercase, price is a negative integer.
    """
    expense = session.scalars(select(Expense)).first()
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=expense.id),
        data={
            "name": NAME,
            "price": -56,
            "form_disabled": True,
        },
    )
    assert "number must be positive" in response.text


def test_update_expense_serve_template_404(client, session):
    """Case: user requests update of a nonexistant expense.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.update_expense.format(expense_id=1))
    assert response.status_code == 404


@patch.object(ExpensesRepo, "update", raise_always, fill_db)
def test_update_expense_exception(client):
    """Case: any exception is thrown."""
    response = client.post(
        SETTINGS.urls.update_expense.format(expense_id=1),
        data={
            "name": NAME,
            "price": -56,
            "form_disabled": True,
        },
    )
    assert response.status_code == 501
    assert "exception" in response.text
