import datetime
from copy import copy
from unittest.mock import patch

from fastapi import status
from sqlalchemy import func, select

from app.exceptions import (NotIntegerError, NotPositiveValueError,
                            SpendingOverBalanceError, ValueTooLargeError)
from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_datetime_without_seconds
from tests.conftest import clean_db, get_newly_created_payment, raise_always
from tests.conftest_helpers import check_created_payment

NAME = "milk"
PRICE = 350


def test_template(client):
    """Case: endpoint returns form to create an payment."""
    response = client.get(url=SETTINGS.urls.create_payment)
    assert response.status_code == 200
    assert "название" in response.text
    assert "сумма" in response.text
    assert "категория" in response.text


def test_template_no_cookie(client, fill_db):
    client.cookies = {}
    response = client.get(url=SETTINGS.urls.create_payment)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(url=SETTINGS.urls.create_payment)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(url=SETTINGS.urls.create_payment)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_valid_data_localized_date(
    session,
    client,
    payment_create,
    positive_balance,
):
    """Case: endpoint creates an payment in db on valid request."""
    max_id_before = session.scalar(select(func.max(Payment.id)))
    payment_create_check = copy(payment_create)
    payment_create.pop("category_id", None)
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    payment = get_newly_created_payment(max_id_before, session)

    check_created_payment(
        payment_create=payment_create_check, payment=payment, response=response
    )
    clean_db(session)


def test_valid_data_spending_over_balance(
    session,
    client,
    payment_create,
):
    max_id_before = session.scalar(select(func.max(Payment.id)))
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    error = SpendingOverBalanceError(payment_create["price"])
    assert error.detail in response.text
    assert str(error.status_code) in response.text
    assert response.status_code == error.status_code
    max_id_after = session.scalar(select(func.max(Payment.id)))
    assert max_id_before == max_id_after
    clean_db(session)


def test_valid_data_localized_date_is_spending_false(
    session, client, payment_create
):
    """Case: endpoint creates an payment in db on valid request."""
    payment_create = copy(payment_create)
    payment_create["is_spending"] = False
    max_id_before = session.scalar(select(func.max(Payment.id)))
    payment_create_check = copy(payment_create)
    payment_create.pop("category_id", None)

    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    payment = get_newly_created_payment(max_id_before, session)

    check_created_payment(
        payment_create=payment_create_check, payment=payment, response=response
    )


def test_valid_data_non_localized_date(
    session, client, payment_create, positive_balance
):
    """Case: endpoint creates an payment in db on valid request."""
    max_id_before = session.scalar(select(func.max(Payment.id)))
    payment_create_check = copy(payment_create)
    payment_create.pop("category_id", None)

    payment_create["date"] = get_datetime_without_seconds(
        datetime.datetime.now()
    )

    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    payment = get_newly_created_payment(max_id_before, session)
    check_created_payment(
        payment_create=payment_create_check, payment=payment, response=response
    )
    clean_db(session)


def test_invalid_data_negative_price(client, payment_create_no_category):
    """Case: endpoint raises NotPositiveValueError if price is negative."""
    negative_price = -100
    payment_create_no_category["price"] = negative_price
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create_no_category
    )
    assert response.status_code == 422
    assert NotPositiveValueError(negative_price).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment


def test_invalid_data_zero_price(client, payment_create_no_category):
    """Case: endpoint raises NotPositiveValueError if price is zero."""
    zero_price = 0
    payment_create_no_category["price"] = zero_price
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create_no_category
    )
    assert response.status_code == 422
    assert NotPositiveValueError(zero_price).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment


def test_invalid_data_price_any_letters(client, payment_create_no_category):
    """Case: endpoint raises NotIntegerError if price is zero."""
    price_any_string = "lalala"
    payment_create_no_category["price"] = price_any_string
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create_no_category
    )
    assert response.status_code == 422
    assert NotIntegerError(price_any_string).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment


def test_invalid_data_price_too_large(client, payment_create_no_category):
    """Case: endpoint raises ValueTooLargeError if price is zero."""
    price_too_large = 999999978
    payment_create_no_category["price"] = price_too_large
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create_no_category
    )
    assert response.status_code == 422
    assert ValueTooLargeError(price_too_large).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment


@patch.object(
    PaymentRepo,
    "create",
    raise_always,
)
def test_any_other_exception(client, payment_create_no_category):
    """Case: endpoint returns 501.

    Covers any exception other than ValidationError.
    """
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create_no_category
    )
    assert response.status_code == 501
    assert response.template.name == SETTINGS.templates.create_payment


def test_no_cookie(client, fill_db, payment_create):
    client.cookies = {}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, fill_db, stale_token, payment_create):
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, fill_db, wrong_token, payment_create):
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=payment_create
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
