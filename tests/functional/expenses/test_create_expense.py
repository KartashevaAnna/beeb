from unittest.mock import patch

from sqlalchemy import select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from app.utils.enums import ExpenseCategory
from tests.functional.conftest import raise_always

NAME = "milk"
PRICE = 350
CATEGORY = ExpenseCategory.list_names()[0]
EXPENSE_CREATE_VALID_JSON = {
    "name": NAME,
    "price": PRICE,
    "category": CATEGORY,
}


def test_create_expense_template(session, client):
    """Case: endpoint returns form to create an expense."""
    response = client.get(url=SETTINGS.urls.create_expense)
    assert response.status_code == 200
    assert "название" in response.text
    assert "стоимость" in response.text
    assert "категория" in response.text


def test_create_expense_valid_data(session, client):
    """Case: endpoint creates an expense in db on valid request."""
    response = client.post(
        url=SETTINGS.urls.create_expense, data=EXPENSE_CREATE_VALID_JSON
    )
    assert response.status_code == 303

    statement = select(Expense).where(
        Expense.name == NAME,
        Expense.price == PRICE,
        Expense.category == CATEGORY,
    )
    results = session.execute(statement)
    expense = results.scalars().one_or_none()
    assert expense
    assert response.headers.get("location") == SETTINGS.urls.expense.format(
        expense_id=expense.id
    )


def test_create_expense_invalid_data_negative_price(session, client):
    """Case: endpoint raises ValidationError if price is negative."""
    response = client.post(
        url=SETTINGS.urls.create_expense,
        data={"name": NAME, "price": -100, "category": CATEGORY},
    )
    assert response.status_code == 422


def test_create_expense_invalid_data_zero_price(session, client):
    """Case: endpoint raises ValidationError if price is zero."""
    response = client.post(
        url=SETTINGS.urls.create_expense,
        data={"name": NAME, "price": 0, "category": CATEGORY},
    )
    assert response.status_code == 422


@patch.object(ExpensesRepo, "create", raise_always)
def test_create_expense_any_other_exception(session, client):
    """Case: endpoint returns 501.

    Covers any exception other than ValidationError.
    """
    response = client.post(
        url=SETTINGS.urls.create_expense, data=EXPENSE_CREATE_VALID_JSON
    )
    assert response.status_code == 501
