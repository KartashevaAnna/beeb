from unittest.mock import patch

from fastapi import status
from sqlalchemy import select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_readable_price
from tests.conftest import raise_always


def test_payments_normal_function(client, fill_db, session):
    """Case: normal mode.

    Checks that the endpoint returns page
    with payments in context.
    """
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == 200
    all_payments = session.scalars(select(Payment)).all()
    assert len(all_payments) > 2
    payment = all_payments[2]
    assert str(payment.id) in response.text
    assert payment.name in response.text
    assert get_readable_price(payment.price) in response.text


def test_payments_empty_db(client):
    """Case: the database is empty.

    Checks that the endpoint returns page
    with no payments in context.
    """
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == 200
    assert response.context["payments"] == []


@patch.object(PaymentRepo, "read_all", raise_always)
def test_payments_exception(client):
    """Case: any exception is thrown.

    Checks that the endpoint returns an error page.
    """
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code != 200


def test_payments_no_cookie(client, fill_db):
    """Case: normal mode.

    Checks that the endpoint redirects to login if token is missing.
    """
    client.cookies = {}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_payments_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_payments_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
