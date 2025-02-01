from unittest.mock import patch

from app.repositories.expenses import ExpenseRepo
from app.settings import SETTINGS
from tests.functional.conftest import raise_always


def test_expenses_normal_function(client, add_expenses):
    """Case: normal mode, endpoint returns page with expenses in context."""
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    assert "название" in response.text
    assert "стоимость" in response.text
    assert "None" not in response.text


@patch.object(ExpenseRepo, "read_all", raise_always)
def test_expenses_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    assert "Exception" in response.text


def test_expense_normal_function(client, expense):
    response = client.get(SETTINGS.urls.expense.format(expense_id=expense.id))
    assert response.status_code == 200
    assert "expense" in response.text
    assert expense.name in response.text
    assert str(expense.price) in response.text
