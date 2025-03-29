from app.settings import SETTINGS


def test_total_expense(client, fill_db):
    """The database is full.

    The endpoint returns total spent per month.
    """
    response = client.get(SETTINGS.urls.total_expenses)
    assert response.status_code == 200


def test_total_expense_monthly(client, fill_db):
    """The database is full.

    The endpoint returns total spent per month.
    """
    response = client.get(SETTINGS.urls.total_expenses_monthly)
    assert response.status_code == 200
