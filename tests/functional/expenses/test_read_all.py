from types import NoneType
from unittest.mock import patch

from sqlalchemy import select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_readable_price
from tests.functional.conftest import raise_always


def test_expenses_normal_function(client, fill_db, session, total_expenses):
    """Case: normal mode.

    Checks that the endpoint returns page
    with expenses in context.
    """
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    all_expenses = session.scalars(select(Expense))
    for expense in all_expenses:
        assert str(expense.id) in response.text
        assert expense.name.title() in response.text
        assert get_readable_price(expense.price) in response.text
    assert isinstance(total_expenses, int)
    assert get_readable_price(total_expenses) in response.text


def test_expenses_empty_db(client, total_expenses):
    """Case: the database is empty.

    Checks that the endpoint returns page
    with no expenses in context.
    """
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    assert response.context["expenses"] == []
    assert isinstance(total_expenses, NoneType)


@patch.object(ExpensesRepo, "read_all", raise_always)
def test_expenses_exception(client):
    """Case: any exception is thrown.

    Checks that the endpoint returns an error page.
    """
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code != 200
    assert "exception" in response.text
