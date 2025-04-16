from datetime import datetime
from unittest.mock import patch

from sqlalchemy import select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import convert_to_copecks, get_date_from_datetime
from tests.conftest import raise_always

NAME = "milk"
PRICE = 350


def test_create_payment_template(client):
    """Case: endpoint returns form to create an payment."""
    response = client.get(url=SETTINGS.urls.create_payment)
    assert response.status_code == 200
    assert "название" in response.text
    assert "сумма" in response.text
    assert "категория" in response.text


def test_create_payment_valid_data(session, client, category):
    """Case: endpoint creates an payment in db on valid request."""

    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": PRICE,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 303

    statement = select(Payment).where(
        Payment.name == NAME,
        Payment.price == convert_to_copecks(PRICE),
        Payment.category_id == category.id,
    )
    results = session.execute(statement)
    payment = results.scalars().one_or_none()
    assert payment
    assert response.headers.get("location") == SETTINGS.urls.create_payment


def test_create_payment_invalid_data_negative_price(client, category):
    """Case: endpoint raises ValidationError if price is negative."""
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": -100,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 422


def test_create_payment_invalid_data_zero_price(client, category):
    """Case: endpoint raises ValidationError if price is zero."""
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": 0,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 422


@patch.object(
    PaymentRepo,
    "create",
    raise_always,
)
def test_create_payment_any_other_exception(client, category):
    """Case: endpoint returns 501.

    Covers any exception other than ValidationError.
    """
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": PRICE,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 501
