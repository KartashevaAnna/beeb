from unittest.mock import patch

from sqlalchemy import select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS
from tests.conftest import fill_db, raise_always


def test_delete_expense(client, expense, session):
    """Case: endpoint deletes an expense."""
    expense_id = expense.id
    response = client.post(
        SETTINGS.urls.delete_expense.format(expense_id=expense_id),
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.expenses
    session.expire_all()
    deleted_expense = session.scalars(
        select(Expense).where(Expense.id == expense_id)
    ).one_or_none()
    assert not deleted_expense


@patch.object(ExpensesRepo, "delete", raise_always, fill_db)
def test_delete_expense_that_does_not_exist(client):
    """Case: any exception is thrown."""
    response = client.post(SETTINGS.urls.delete_expense.format(expense_id=1))
    assert response.status_code == 501
    assert "exception" in response.text


def test_delete_expense_template(client):
    response = client.get(SETTINGS.urls.delete_expense)
    assert response.status_code == 200
