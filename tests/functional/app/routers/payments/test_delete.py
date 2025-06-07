from unittest.mock import patch

from fastapi import status
from sqlalchemy import select

from app.exceptions import NotOwnerError
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
    assert response.template.name == SETTINGS.templates.read_payment


def test_no_cookie(client, payment):
    payment_id = payment.id
    client.cookies = {}
    response = client.post(
        url=SETTINGS.urls.delete_payment.format(payment_id=payment_id),
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, payment, stale_token):
    payment_id = payment.id
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.delete_payment.format(payment_id=payment_id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, payment, wrong_token):
    payment_id = payment.id
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.delete_payment.format(payment_id=payment_id),
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_user(client, payment, session, update_payment, wrong_user_token):
    client.cookies["token"] = wrong_user_token
    response = client.post(
        SETTINGS.urls.delete_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert response.status_code == NotOwnerError(payment.name).status_code
    assert response.template.name == SETTINGS.templates.delete_payment
    session.expire_all()
    not_deleted_payment = session.get(Payment, payment.id)
    assert not_deleted_payment
