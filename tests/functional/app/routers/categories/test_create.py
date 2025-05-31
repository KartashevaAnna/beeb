from copy import copy
from unittest.mock import patch

from fastapi import status
from sqlalchemy import select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import clean_db, delete_category, raise_always


def test_template(client):
    """Case: endpoint returns form to create a category."""
    response = client.get(url=SETTINGS.urls.create_category)
    assert response.status_code == status.HTTP_200_OK
    assert "имя" in response.text


def test_template_no_cookie(client, fill_db):
    client.cookies = {}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, fill_db, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, fill_db, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(SETTINGS.urls.payments)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_valid_data(session, client, category_create):
    """Case: endpoint creates a category in db on valid request."""
    delete_category(session)
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )

    assert response.status_code == status.HTTP_303_SEE_OTHER
    statement = select(Category).where(Category.name == category_create["name"])
    results = session.execute(statement)
    category = results.scalars().one_or_none()
    assert category
    assert response.headers.get("location") == SETTINGS.urls.categories
    clean_db(session)


def test_invalid_name(client, category_create, session):
    """Case: endpoint fails creating a category in db with invalid request."""
    delete_category(session)
    category_create = copy(category_create)
    category_create["name"] = None
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_data(client, category_create, session):
    """Case: endpoint fails creating a category in db with invalid request."""
    delete_category(session)
    category_create = copy(category_create)
    category_create.pop("name", None)
    category_create["unexpected_parameter"] = "hello_world"
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_duplicate_category(client, category, category_create, session):
    """Case: endpoint refuses creating a category with a duplicate name."""
    delete_category(session)
    category_create = copy(category_create)
    category_create["name"] = category.name
    client.post(url=SETTINGS.urls.create_category, data=category_create)
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


@patch.object(
    CategoryRepo,
    "create",
    raise_always,
)
def test_any_other_exception(client, category_create, session):
    delete_category(session)
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED


def test_no_cookie(client, category_create, session):
    delete_category(session)
    client.cookies = {}
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token(client, stale_token, category_create, session):
    delete_category(session)
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token(client, wrong_token, category_create, session):
    delete_category(session)
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
