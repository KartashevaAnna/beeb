from unittest.mock import patch

from sqlalchemy import func, select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_readable_price
from tests.conftest import expense, raise_always


def test_expense_normal_function(client, expense, session):
    """Case: normal mode.

    Checks that the endpoint returns page
    with one expense in context.
    """
    response = client.get(SETTINGS.urls.expense.format(expense_id=expense.id))
    assert response.status_code == 200
    assert str(expense.id) in response.text
    assert expense.name.title() in response.text
    assert get_readable_price(expense.price) in response.text
    assert expense.expense_category.name in response.text


def test_expense_404(client, session, fill_db):
    """Case: user request a nonexistant id.

    Checks that the endpoint returns a 404 status code.
    """
    max_expense_id = session.scalar(select(func.max(Expense.id)))
    non_existing_expense_id = max_expense_id + 1
    response = client.get(
        SETTINGS.urls.expense.format(expense_id=non_existing_expense_id)
    )
    assert response.status_code == 404


def test_expense_empty_db_404(client):
    """Case: the database is empty.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.expense.format(expense_id=1))
    assert response.status_code == 404


@patch.object(ExpensesRepo, "read", raise_always, expense)
def test_expense_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.expense.format(expense_id=1))
    assert response.status_code != 200
    assert "exception" in response.text
