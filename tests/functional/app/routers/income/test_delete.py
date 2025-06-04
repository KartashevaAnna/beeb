from sqlalchemy import select
from fastapi import status

from app.exceptions import NotOwnerError
from app.models import Income
from app.settings import SETTINGS


def test_delete(client, income, session):
    income_id = income.id
    response = client.post(
        SETTINGS.urls.delete_income.format(income_id=income_id),
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    deleted_payment = session.scalars(
        select(Income).where(Income.id == income_id)
    ).one_or_none()
    assert not deleted_payment


def test_no_cookie(client, income):
    income_id = income.id
    client.cookies = {}
    response = client.post(
        SETTINGS.urls.delete_income.format(income_id=income_id),
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, income, stale_token):
    income_id = income.id
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.delete_income.format(income_id=income_id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, income, wrong_token):
    income_id = income.id
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.delete_income.format(income_id=income_id),
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_user(client, income, session, wrong_user_token):
    income_id = income.id
    client.cookies["token"] = wrong_user_token
    response = client.post(
        url=SETTINGS.urls.delete_income.format(income_id=income_id),
    )
    assert response.status_code == NotOwnerError(income.name).status_code
    assert response.template.name == SETTINGS.templates.delete_payment
    session.expire_all()
    not_deleted_payment = session.get(Income, income.id)
    assert not_deleted_payment
