from fastapi import status

from app.settings import SETTINGS
from tests.conftest import clean_db


def test_template(client, income, session):
    response = client.get(
        SETTINGS.urls.update_income.format(income_id=income.id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert income.name in response.text
    assert str(income.amount // 100) in response.text


def test_template_no_cookie(client, income, session):
    client.cookies = {}
    response = client.get(
        SETTINGS.urls.update_income.format(income_id=income.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, income, session):
    pass
