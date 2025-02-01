from unittest.mock import patch

from app.repositories.expenses import ExpenseRepo
from app.settings import SETTINGS
from tests.constants import EXPENSES
from tests.functional.conftest import raise_always


def test_expenses_normal_function(client, add_expenses):
    """Case: normal mode, endpoint returns page with expenses in context."""
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    assert "название" in response.text
    assert "стоимость" in response.text
    assert "None" not in response.text
    assert EXPENSES[0]["name"] in response.text
    assert str(EXPENSES[-1]["price"]) in response.text


@patch.object(ExpenseRepo, "read_all", raise_always)
def test_expenses_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.expenses)
    assert response.status_code == 200
    assert "Exception" in response.text
