import datetime
from copy import deepcopy
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session

from app.exceptions import (
    NotIntegerError,
    NotPositiveValueError,
    SpendingOverBalanceError,
    ValueTooLargeError,
)
from app.models import Income, Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_datetime_without_seconds
from tests.conftest import get_newly_created_payment, raise_always
from tests.conftest_helpers import check_created_payment

NAME = "milk"
amount = 350


def test_template_food(client):
    """Case: endpoint returns form to create an payment."""
    response = client.get(url=SETTINGS.urls.create_payment_food)
    assert response.status_code == status.HTTP_200_OK
    assert "имя" in response.text
    assert "рублей" in response.text
    assert "категория" in response.text
    assert "грамм" in response.text
    assert "штук" not in response.text


def test_template_non_food(client):
    """Case: endpoint returns form to create an payment."""
    response = client.get(url=SETTINGS.urls.create_payment_non_food)
    assert response.status_code == status.HTTP_200_OK
    assert "имя" in response.text
    assert "рублей" in response.text
    assert "категория" in response.text
    assert "штук" in response.text
    assert "грамм" not in response.text


def test_template_no_cookie_food(client, fill_db):
    client.cookies = {}
    response = client.get(url=SETTINGS.urls.create_payment_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_no_cookie_non_food(client, fill_db):
    client.cookies = {}
    response = client.get(url=SETTINGS.urls.create_payment_non_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token_food(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(url=SETTINGS.urls.create_payment_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token_non_food(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(url=SETTINGS.urls.create_payment_non_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token_food(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(url=SETTINGS.urls.create_payment_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token_non_food(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(url=SETTINGS.urls.create_payment_non_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_valid_data_localized_date_food(
    session,
    client,
    create_payment_food,
    positive_balance,
):
    max_id_before = session.scalar(select(func.max(Payment.id)))
    payment_create_check = deepcopy(create_payment_food)
    create_payment_food.pop("category_id", None)
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    payment = get_newly_created_payment(max_id_before, session)

    check_created_payment(
        create_payment=payment_create_check,
        payment=payment,
        response=response,
    )


def test_valid_data_localized_date_non_food(
    session,
    client,
    create_payment_non_food,
    positive_balance,
):
    max_id_before = session.scalar(select(func.max(Payment.id)))
    check_payment_create = deepcopy(create_payment_non_food)
    create_payment_non_food.pop("category_id", None)
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data=create_payment_non_food,
    )
    payment = get_newly_created_payment(max_id_before, session)

    check_created_payment(
        create_payment=check_payment_create, payment=payment, response=response
    )


def test_valid_data_non_localized_date_food(
    session: Session,
    client: TestClient,
    create_payment_food: dict,
    positive_balance: Income,
):
    max_id_before = session.scalar(select(func.max(Payment.id)))
    payment_create_check = deepcopy(create_payment_food)
    create_payment_food.pop("category_id", None)
    create_payment_food["date"] = get_datetime_without_seconds(
        datetime.datetime.now()
    )
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    payment = get_newly_created_payment(max_id_before, session)
    check_created_payment(
        create_payment=payment_create_check, payment=payment, response=response
    )


def test_valid_data_non_localized_date_non_food(
    session: Session,
    client: TestClient,
    create_payment_non_food: dict,
    positive_balance: Income,
):
    max_id_before = session.scalar(select(func.max(Payment.id)))
    payment_create_check = deepcopy(create_payment_non_food)
    create_payment_non_food.pop("category_id", None)
    create_payment_non_food["date"] = get_datetime_without_seconds(
        datetime.datetime.now()
    )
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data=create_payment_non_food,
    )
    payment = get_newly_created_payment(max_id_before, session)
    check_created_payment(
        create_payment=payment_create_check, payment=payment, response=response
    )


def test_invalid_data_negative_amount_food(
    client: TestClient, create_payment_food: dict
):
    """Case: endpoint raises NotPositiveValueError if amount is negative."""
    negative_amount = -100
    create_payment_food["amount"] = negative_amount
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert (
        response.status_code
        == NotPositiveValueError(negative_amount).status_code
    )
    assert NotPositiveValueError(negative_amount).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_negative_amount_non_food(
    client: TestClient, create_payment_non_food: dict
):
    negative_amount = -100
    create_payment_non_food["amount"] = negative_amount
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert (
        response.status_code
        == NotPositiveValueError(negative_amount).status_code
    )
    assert NotPositiveValueError(negative_amount).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_zero_amount_food(
    client: TestClient, create_payment_food: dict
):
    zero_amount = 0
    create_payment_food["amount"] = zero_amount
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert NotPositiveValueError(zero_amount).detail in response.text
    assert (
        response.status_code == NotPositiveValueError(zero_amount).status_code
    )
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_zero_amount_non_food(
    client: TestClient, create_payment_non_food: dict
):
    """Case: endpoint raises NotPositiveValueError if amount is zero."""
    zero_amount = 0
    create_payment_non_food["amount"] = zero_amount
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data=create_payment_non_food,
    )
    assert NotPositiveValueError(zero_amount).detail in response.text
    assert (
        response.status_code == NotPositiveValueError(zero_amount).status_code
    )
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_amount_any_letters_food(
    client: TestClient, create_payment_food: dict
):
    """Case: endpoint raises NotIntegerError if amount is zero."""
    amount_any_string = "lalala"
    create_payment_food["amount"] = amount_any_string
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert (
        response.status_code == NotIntegerError(amount_any_string).status_code
    )
    assert NotIntegerError(amount_any_string).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_amount_any_letters_non_food(
    client: TestClient, create_payment_non_food: dict
):
    """Case: endpoint raises NotIntegerError if amount is zero."""
    amount_any_string = "lalala"
    create_payment_non_food["amount"] = amount_any_string
    response = client.post(
        url=SETTINGS.urls.create_payment,
        data=create_payment_non_food,
    )
    assert (
        response.status_code == NotIntegerError(amount_any_string).status_code
    )
    assert NotIntegerError(amount_any_string).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_amount_too_large_food(
    client: TestClient, create_payment_food: dict
):
    amount_too_large = 999999978
    create_payment_food["amount"] = amount_too_large
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert (
        response.status_code == ValueTooLargeError(amount_too_large).status_code  # noqa: E501
    )
    assert ValueTooLargeError(amount_too_large).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_amount_too_large_non_food(
    client: TestClient, create_payment_non_food: dict
):
    amount_too_large = 999999978
    create_payment_non_food["amount"] = amount_too_large
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert (
        response.status_code == ValueTooLargeError(amount_too_large).status_code  # noqa: E501
    )
    assert ValueTooLargeError(amount_too_large).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_negative_grams_food(
    client: TestClient, create_payment_food: dict
):
    negative_grams = -100
    create_payment_food["grams"] = negative_grams
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert (
        response.status_code
        == NotPositiveValueError(negative_grams).status_code
    )
    assert NotPositiveValueError(negative_grams).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_zero_grams_food(
    client: TestClient, create_payment_food: dict
):
    zero_grams = 0
    create_payment_food["grams"] = zero_grams
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert NotPositiveValueError(zero_grams).detail in response.text
    assert response.status_code == NotPositiveValueError(zero_grams).status_code
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_grams_any_letters_food(
    client: TestClient, create_payment_food: dict
):
    grams_any_string = "lalala"
    create_payment_food["grams"] = grams_any_string
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert response.status_code == NotIntegerError(grams_any_string).status_code
    assert NotIntegerError(grams_any_string).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_grams_too_large(
    client: TestClient, create_payment_food: dict
):
    grams_too_large = 999999978
    create_payment_food["grams"] = grams_too_large
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert (
        response.status_code == ValueTooLargeError(grams_too_large).status_code
    )
    assert ValueTooLargeError(grams_too_large).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_invalid_data_quantity_non_food(
    client: TestClient, create_payment_non_food: dict
):
    negative_quantity = -100
    create_payment_non_food["quantity"] = negative_quantity
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert (
        response.status_code
        == NotPositiveValueError(negative_quantity).status_code
    )
    assert NotPositiveValueError(negative_quantity).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_zero_quantity_non_food(
    client: TestClient, create_payment_non_food: dict
):
    zero_quantity = 0
    create_payment_non_food["quantity"] = zero_quantity
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert NotPositiveValueError(zero_quantity).detail in response.text
    assert (
        response.status_code == NotPositiveValueError(zero_quantity).status_code
    )
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_quantity_any_letters_non_food(
    client: TestClient, create_payment_non_food: dict
):
    quantity_any_string = "lalala"
    create_payment_non_food["quantity"] = quantity_any_string
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert (
        response.status_code == NotIntegerError(quantity_any_string).status_code
    )
    assert NotIntegerError(quantity_any_string).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_invalid_data_quantity_too_large(
    client: TestClient, create_payment_non_food: dict
):
    quantity_too_large = 999999978
    create_payment_non_food["quantity"] = quantity_too_large
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert (
        response.status_code
        == ValueTooLargeError(quantity_too_large).status_code
    )
    assert ValueTooLargeError(quantity_too_large).detail in response.text
    assert response.template.name == SETTINGS.templates.create_payment_non_food


@patch.object(
    PaymentRepo,
    "create",
    raise_always,
)
def test_any_other_exception_food(
    client: TestClient, create_payment_food: dict
):
    """Case: endpoint returns 501.

    Covers any exception other than ValidationError.
    """
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert response.status_code == 501
    assert response.template.name == SETTINGS.templates.create_payment_food


def test_no_cookie_food(
    client: TestClient, fill_db: None, create_payment_food: dict
):
    client.cookies = {}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token_food(
    client: TestClient,
    fill_db: None,
    stale_token,
    create_payment_food: dict,
):
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token_food(
    client: TestClient,
    fill_db: None,
    wrong_token,
    create_payment_food: dict,
):
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_food
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


@patch.object(
    PaymentRepo,
    "create",
    raise_always,
)
def test_any_other_exception_non_food(
    client: TestClient, create_payment_non_food: dict
):
    """Case: endpoint returns 501.

    Covers any exception other than ValidationError.
    """
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert response.status_code == 501
    assert response.template.name == SETTINGS.templates.create_payment_non_food


def test_no_cookie_non_food(
    client: TestClient, fill_db: None, create_payment_non_food: dict
):
    client.cookies = {}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token_non_food(
    client: TestClient,
    fill_db: None,
    stale_token,
    create_payment_non_food: dict,
):
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token_non_food(
    client: TestClient,
    fill_db: None,
    wrong_token,
    create_payment_non_food: dict,
):
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.create_payment, data=create_payment_non_food
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
