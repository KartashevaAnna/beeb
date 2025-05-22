from unittest.mock import patch

from fastapi import status
from sqlalchemy import select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_readable_price
from tests.conftest import TEST_USER_ID, raise_always


def test_normal_function(client, fill_db, session):
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == 200
    all_payments = session.scalars(select(Payment)).all()
    assert len(all_payments) > 2
    payment = all_payments[2]
    assert str(payment.id) in response.text
    assert payment.name in response.text
    assert get_readable_price(payment.price) in response.text
    assert payment.user_id == TEST_USER_ID


def test_empty_db(client):
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == 200
    assert response.context["payments"] == []


@patch.object(PaymentRepo, "read_all", raise_always)
def test_any_other_exception(client):
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code != 200
    assert response.template.name == SETTINGS.templates.read_payments


def test_no_cookie(client, fill_db):
    client.cookies = {}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
