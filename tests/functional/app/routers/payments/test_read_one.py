from unittest.mock import patch

from sqlalchemy import func, select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from tests.conftest import payment, raise_always


def test_payment_normal_function(client, payment):
    """Case: normal mode.

    Checks that the endpoint returns page
    with one payment in context.
    """
    response = client.get(SETTINGS.urls.payment.format(payment_id=payment.id))
    assert response.status_code == 200
    assert str(payment.id) in response.text
    assert payment.name.title() in response.text
    assert str(payment.price // 100) in response.text


def test_payment_404(client, session, fill_db):
    """Case: user request a nonexistant id.

    Checks that the endpoint returns a 404 status code.
    """
    max_payment_id = session.scalar(select(func.max(Payment.id)))
    non_existing_payment_id = max_payment_id + 1
    response = client.get(
        SETTINGS.urls.payment.format(payment_id=non_existing_payment_id)
    )
    assert response.status_code == 404


def test_payment_empty_db_404(client):
    """Case: the database is empty.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.payment.format(payment_id=1))
    assert response.status_code == 404


@patch.object(PaymentRepo, "read", raise_always, payment)
def test_payment_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.payment.format(payment_id=1))
    assert response.status_code != 200
