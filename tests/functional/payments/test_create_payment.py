from datetime import datetime
from unittest.mock import patch

from sqlalchemy import select

from app.exceptions import (
    NotIntegerError,
    NotPositiveValueError,
    ValueTooLargeError,
)
from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import (
    convert_to_copecks,
    get_date_from_datetime,
    get_datetime_without_seconds,
)
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


def test_create_payment_valid_data_localized_date(session, client, category):
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


def test_create_payment_valid_data_non_localized_date(
    session, client, category
):
    """Case: endpoint creates an payment in db on valid request."""

    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": PRICE,
            "category": category.name,
            "date": get_datetime_without_seconds(datetime.now()),
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
    """Case: endpoint raises NotPositiveValueError if price is negative."""
    negative_price = -100
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": negative_price,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 422
    assert NotPositiveValueError(negative_price).detail in response.text


def test_create_payment_invalid_data_zero_price(client, category):
    """Case: endpoint raises NotPositiveValueError if price is zero."""
    zero_price = 0
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": zero_price,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 422
    assert NotPositiveValueError(zero_price).detail in response.text


def test_create_payment_invalid_data_price_any_letters(client, category):
    """Case: endpoint raises NotIntegerError if price is zero."""
    price_any_string = "lalala"
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": price_any_string,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 422
    assert NotIntegerError(price_any_string).detail in response.text


def test_create_payment_invalid_data_price_too_large(client, category):
    """Case: endpoint raises ValueTooLargeError if price is zero."""
    price_too_large = 999999978
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data={
            "name": NAME,
            "price": price_too_large,
            "category": category.name,
            "date": get_date_from_datetime(datetime.now()),
        },
    )
    assert response.status_code == 422
    assert ValueTooLargeError(price_too_large).detail in response.text


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
