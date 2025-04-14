from app.settings import SETTINGS


def test_total_payment(client, fill_db):
    """The database is full.

    The endpoint returns total spent per month.
    """
    response = client.get(SETTINGS.urls.total_payments)
    assert response.status_code == 200


def test_total_payment_monthly(client, fill_db):
    """The database is full.

    The endpoint returns total spent per month.
    """
    response = client.get(SETTINGS.urls.total_payments_monthly)
    assert response.status_code == 200
