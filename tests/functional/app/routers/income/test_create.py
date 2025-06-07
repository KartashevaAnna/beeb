from copy import deepcopy
import datetime
from fastapi import status
from sqlalchemy import func, select
from app.exceptions import (
    NotIntegerError,
    NotPositiveValueError,
    ValueTooLargeError,
)
from app.models import Income
from app.settings import SETTINGS
from app.utils.tools.helpers import (
    convert_to_copecks,
    get_datetime_without_seconds,
)
from tests.conftest import get_all_income, get_newly_created_income
from tests.conftest_helpers import check_created_income


def test_template(client):
    """Case: endpoint returns form to create an income."""
    response = client.get(url=SETTINGS.urls.create_income)
    assert response.status_code == status.HTTP_200_OK
    assert "имя" in response.text
    assert "рублей" in response.text


def test_template_no_cookie(client, fill_db):
    client.cookies = {}
    response = client.get(url=SETTINGS.urls.create_income)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(url=SETTINGS.urls.create_income)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(url=SETTINGS.urls.create_income)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_valid_data_localized_date(session, client, create_income):
    create_income_check = deepcopy(create_income)
    max_id_before = session.scalar(select(func.max(Income.id)))
    response = client.post(
        url=SETTINGS.urls.create_income,
        data=create_income,
    )
    assert get_all_income(session)
    income = get_newly_created_income(max_id_before, session)
    check_created_income(
        create_income=create_income_check, income=income, response=response
    )


def test_valid_data_non_localized_date(session, client, create_income):
    max_id_before = session.scalar(select(func.max(Income.id)))
    income_create_check = deepcopy(create_income)
    create_income["date"] = get_datetime_without_seconds(
        datetime.datetime.now()
    )
    response = client.post(url=SETTINGS.urls.create_income, data=create_income)
    income = get_newly_created_income(max_id_before, session)
    check_created_income(
        create_income=income_create_check, income=income, response=response
    )


def test_invalid_data_negative_amount(client, create_income):
    """Case: endpoint raises NotPositiveValueError if amount is negative."""
    negative_amount = -100
    create_income["amount"] = negative_amount
    response = client.post(url=SETTINGS.urls.create_income, data=create_income)
    assert (
        response.status_code
        == NotPositiveValueError(negative_amount).status_code
    )
    assert NotPositiveValueError(negative_amount).detail in response.text
    assert response.template.name == SETTINGS.templates.create_income


def test_invalid_data_zero_amount(client, create_income):
    """Case: endpoint raises NotPositiveValueError if amount is zero."""
    zero_amount = 0
    create_income["amount"] = zero_amount
    response = client.post(
        url=SETTINGS.urls.create_income,
        data=create_income,
    )
    assert NotPositiveValueError(zero_amount).detail in response.text
    assert (
        response.status_code == NotPositiveValueError(zero_amount).status_code
    )
    assert response.template.name == SETTINGS.templates.create_income


def test_invalid_data_amount_any_letters(client, create_income):
    """Case: endpoint raises NotIntegerError if amount is zero."""
    amount_any_string = "lalala"
    create_income["amount"] = amount_any_string
    response = client.post(url=SETTINGS.urls.create_income, data=create_income)
    assert (
        response.status_code == NotIntegerError(amount_any_string).status_code
    )
    assert NotIntegerError(amount_any_string).detail in response.text
    assert response.template.name == SETTINGS.templates.create_income


def test_invalid_data_amount_too_large(client, create_income):
    amount_too_large = 999999978
    create_income["amount"] = amount_too_large
    response = client.post(url=SETTINGS.urls.create_income, data=create_income)
    assert (
        response.status_code == ValueTooLargeError(amount_too_large).status_code
    )
    assert ValueTooLargeError(amount_too_large).detail in response.text
    assert response.template.name == SETTINGS.templates.create_income
