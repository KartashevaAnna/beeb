from unittest.mock import patch

from sqlalchemy import func, select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from tests.functional.conftest import fill_db, raise_always


def test_expense_normal_function(client, fill_db, session):
    """Case: normal mode, endpoint returns page with one expense in context."""
    expense = session.scalars(select(Expense)).first()
    response = client.get(SETTINGS.urls.expense.format(expense_id=expense.id))
    assert response.status_code == 200
    assert str(expense.id) in response.text
    assert expense.name in response.text
    assert str(expense.price) in response.text


def test_expense_404(client, fill_db, session):
    """Case: user request a nonexistant id, endpoint returns page with no expense in context."""
    max_expense_id = session.scalar(select(func.max(Expense.id)))
    non_existing_expense_id = max_expense_id + 1
    response = client.get(SETTINGS.urls.expense.format(expense_id=non_existing_expense_id))
    assert response.status_code == 404


def test_expense_empty_db_404(client):
    """Case: the database is empty, endpoint returns page with no expense in context."""
    response = client.get(SETTINGS.urls.expense.format(expense_id=1))
    assert response.status_code == 404


@patch.object(ExpensesRepo, "read", raise_always, fill_db)
def test_expense_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.expense.format(expense_id=1))
    assert response.status_code != 200
    assert "exception" in response.text
