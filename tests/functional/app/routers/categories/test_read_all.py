from unittest.mock import patch

from fastapi import status
from sqlalchemy import select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import raise_always


def test_normal_mode(client, fill_db, session):
    response = client.get(SETTINGS.urls.categories)
    assert response.status_code == status.HTTP_200_OK
    all_categories = session.scalars(select(Category)).all()
    assert len(all_categories) > 2
    category = all_categories[2]
    assert category.name in response.text


def test_empty_db(client):
    response = client.get(SETTINGS.urls.categories)
    assert response.status_code == status.HTTP_200_OK
    assert response.context["categories"] == []


@patch.object(CategoryRepo, "read_all", raise_always)
def test_any_other_exception(client):
    response = client.get(SETTINGS.urls.categories)
    assert response.status_code != status.HTTP_200_OK


def test_no_cookie(client, fill_db, session):
    client.cookies = {}
    response = client.get(url=SETTINGS.urls.categories)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(url=SETTINGS.urls.categories)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(url=SETTINGS.urls.categories)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
