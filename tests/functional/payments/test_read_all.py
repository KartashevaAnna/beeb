from types import NoneType
from unittest.mock import patch

from sqlalchemy import select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_readable_price
from tests.conftest import raise_always


def test_payments_normal_function(client, fill_db, session, total_payments):
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
    assert payment.name.title() in response.text
    assert get_readable_price(payment.price) in response.text
    assert isinstance(total_payments, int)
    assert get_readable_price(total_payments) in response.text


def test_payments_empty_db(client, total_payments):
    """Case: the database is empty.

    Checks that the endpoint returns page
    with no payments in context.
    """
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == 200
    assert response.context["payments"] == []
    assert isinstance(total_payments, NoneType)


@patch.object(PaymentRepo, "read_all", raise_always)
def test_payments_exception(client):
    """Case: any exception is thrown.

    Checks that the endpoint returns an error page.
    """
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code != 200
