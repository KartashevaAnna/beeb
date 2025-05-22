from unittest.mock import patch

from fastapi import status
from sqlalchemy import func, select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import payment, raise_always


def test_normal_mode(client, category):
    response = client.get(
        SETTINGS.urls.category.format(category_id=category.id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert category.name in response.text


def test_non_existant_id(client, session, fill_db):
    max_category_id = session.scalar(select(func.max(Category.id)))
    non_existing_category_id = max_category_id + 1
    response = client.get(
        SETTINGS.urls.category.format(category_id=non_existing_category_id)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_empty_db_404(client):
    response = client.get(SETTINGS.urls.category.format(category_id=1))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch.object(CategoryRepo, "read", raise_always, payment)
def test_category_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.category.format(category_id=1))
    assert response.status_code != status.HTTP_200_OK


def test_no_cookie(client, category):
    client.cookies = {}
    response = client.get(
        SETTINGS.urls.category.format(category_id=category.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, category, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(
        SETTINGS.urls.category.format(category_id=category.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, category, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(
        SETTINGS.urls.category.format(category_id=category.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
