from copy import deepcopy
from fastapi import status

from app.exceptions import NotPositiveValueError
from app.models import Income
from app.schemas.income import IncomeUpdate
from app.settings import SETTINGS
from tests.conftest import TEST_INCOME_UPDATED_NAME
from tests.conftest_helpers import check_updated_income


def test_template(client, income):
    response = client.get(
        SETTINGS.urls.update_income.format(income_id=income.id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert income.name in response.text
    assert str(income.amount // 100) in response.text


def test_template_no_cookie(client, income):
    client.cookies = {}
    response = client.get(
        SETTINGS.urls.update_income.format(income_id=income.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, income, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(
        SETTINGS.urls.update_income.format(income_id=income.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, income, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(
        SETTINGS.urls.update_income.format(income_id=income.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_no_cookie(client, income, update_income):
    client.cookies = {}
    response = client.post(
        SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, income, stale_token, update_income):
    client.cookies = {"token": stale_token}
    response = client.post(
        SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, income, wrong_token, update_income):
    client.cookies = {"token": wrong_token}
    response = client.post(
        SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_update_name_name_lowercase_amount_int(
    client, income, update_income, session
):
    name_before_update = income.name
    response = client.post(
        url=SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_income = session.get(Income, income.id)
    assert name_before_update != updated_income.name


def test_title_amount_int(client, income, update_income, session):
    update_income = deepcopy(update_income)
    update_income["name"] = TEST_INCOME_UPDATED_NAME.title()
    response = client.post(
        url=SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    session.expire_all()
    updated_income = session.get(Income, income.id)
    check_updated_income(updated_income, update_income, response)


def test_name_upper_amount_int(client, income, update_income, session):
    update_income = deepcopy(update_income)
    update_income["name"] = TEST_INCOME_UPDATED_NAME.upper()
    response = client.post(
        url=SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    session.expire_all()
    updated_income = session.get(Income, income.id)
    check_updated_income(updated_income, update_income, response)


def test_name_lowercase_amount_frontend(client, income, update_income, session):
    update_income = deepcopy(update_income)
    update_income["amount"] = "65₽"
    response = client.post(
        url=SETTINGS.urls.update_income.format(income_id=income.id),
        data=update_income,
    )
    session.expire_all()
    updated_income = session.get(Income, income.id)
    check_updated_income(updated_income, update_income, response)


# def test_name_lowercase_amount_int_zero(client, income, update_income, session):
#     update_income = deepcopy(update_income)
#     update_income["amount"] = -100
#     response = client.post(
#         url=SETTINGS.urls.update_income.format(income_id=income.id),
#         data=update_income,
#     )
#     assert NotPositiveValueError(-100).detail in response.text
