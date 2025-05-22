import datetime

from app.settings import SETTINGS


def test_total_payment(client, fill_db):
    response = client.get(SETTINGS.urls.payments_dashboard)
    assert response.status_code == 200


def test_total_payment_yearly(client, fill_db):
    current_year = datetime.datetime.now().year
    response = client.get(f"{SETTINGS.urls.payments_dashboard}/{current_year}")
    assert response.status_code == 200
