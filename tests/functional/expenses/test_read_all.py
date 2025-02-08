from unittest.mock import patch

from sqlalchemy import select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from tests.functional.conftest import raise_always


def test_expenses_normal_function(client, fill_db, session):
    """Case: normal mode, endpoint returns page with expenses in context."""
    response = client.get(SETTINGS.urls.expenses)
    all_expenses = session.scalars(select(Expense))
    assert response.status_code == 200
    for expense in all_expenses:
        assert str(expense.id) in response.text
        assert expense.name in response.text
        assert str(expense.price) in response.text


def test_expenses_empty_db(client):
    """Case: the database is empty, endpoint returns page with no expenses in context."""
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    assert response.context["expenses"] == []


@patch.object(ExpensesRepo, "read_all", raise_always)
def test_expenses_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code != 200
    assert "exception" in response.text
