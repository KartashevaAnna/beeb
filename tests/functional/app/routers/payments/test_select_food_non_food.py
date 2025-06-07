from fastapi import status
from app.settings import SETTINGS


def test_template(client):
    response = client.get(SETTINGS.urls.select_food_non_food)
    assert response.status_code == status.HTTP_200_OK
    assert "Еда" in response.text
    assert "Вещь" in response.text


def test_template_no_cookie(client, fill_db):
    client.cookies = {}
    response = client.get(url=SETTINGS.urls.select_food_non_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(url=SETTINGS.urls.select_food_non_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(url=SETTINGS.urls.select_food_non_food)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
