from unittest.mock import patch

from sqlalchemy import select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from tests.conftest import fill_db, raise_always


def test_delete_payment(client, payment, session):
    """Case: endpoint deletes an payment."""
    payment_id = payment.id
    response = client.post(
        SETTINGS.urls.delete_payment.format(payment_id=payment_id),
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    deleted_payment = session.scalars(
        select(Payment).where(Payment.id == payment_id)
    ).one_or_none()
    assert not deleted_payment


@patch.object(PaymentRepo, "delete", raise_always, fill_db)
def test_delete_payment_that_does_not_exist(client):
    """Case: any exception is thrown."""
    response = client.post(SETTINGS.urls.delete_payment.format(payment_id=1))
    assert response.status_code == 501
    assert "exception" in response.text


def test_delete_payment_template(client):
    response = client.get(SETTINGS.urls.delete_payment)
    assert response.status_code == 200
