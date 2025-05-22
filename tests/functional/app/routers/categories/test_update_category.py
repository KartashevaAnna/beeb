from unittest.mock import patch

from fastapi import status

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import (
    clean_db,
    get_categories,
    raise_always,
)

NAME = "exotic_category"


def test_template(client, category, session):
    """Case: endpoint returns form to update a category."""
    category_id = category.id
    response = client.get(
        SETTINGS.urls.update_category.format(category_id=category_id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert category.name in response.text
    clean_db(session)


def test_template_no_cookie(client, category, session):
    category_id = category.id
    client.cookies = {}
    response = client.get(
        url=SETTINGS.urls.update_category.format(category_id=category_id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)


def test_template_stale_token(client, category, session, stale_token):
    category_id = category.id
    client.cookies = {"token": stale_token}
    response = client.get(
        url=SETTINGS.urls.update_category.format(category_id=category_id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, category, session, wrong_token):
    category_id = category.id
    client.cookies = {"token": wrong_token}
    response = client.get(
        url=SETTINGS.urls.update_category.format(category_id=category_id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)


def test_update_name(client, category, category_create, session):
    """Case: endpoint updates a category."""
    category_id = category.id
    category_create["name"] = NAME
    response = client.post(
        SETTINGS.urls.update_category.format(
            category_id=category_id,
        ),
        data=category_create,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.categories
    session.expire_all()
    updated_category = session.get(Category, category_id)
    assert updated_category
    assert category_id == updated_category.id
    assert updated_category.name == NAME
    assert updated_category.is_active == category.is_active
    clean_db(session)


def test_change_status(client, category, category_create, session):
    """Case: endpoint updates a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data=category_create,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.categories
    clean_db(session)


def test_uplicate_name(client, categories, category_create, session):
    """Case: endpoint refuses updating a category."""
    categories = get_categories(session)
    category_id = categories[0].id
    category_create["name"] = categories[1].name
    category_create["user_id"] = categories[1].user_id
    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data=category_create,
    )
    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    clean_db(session)


def test_name_is_None(client, category, category_create, session):
    """Case: endpoint refuses updating a category."""
    category_id = category.id
    category_create["name"] = None
    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data=category_create,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    clean_db(session)


def test_404(client):
    response = client.get(SETTINGS.urls.update_category.format(category_id=1))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch.object(CategoryRepo, "update", raise_always)
def test_any_other_exception(client, category, session):
    category_id = category.id
    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": NAME, "is_active": category.is_active},
    )
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    clean_db(session)


def test_no_cookie(client, category, category_create, session):
    category_id = category.id
    client.cookies = {}
    response = client.post(
        url=SETTINGS.urls.update_category.format(category_id=category_id),
        data=category_create,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)


def test_stale_token(client, category, category_create, session, stale_token):
    category_id = category.id
    client.cookies = {"token": stale_token}
    response = client.post(
        url=SETTINGS.urls.update_category.format(category_id=category_id),
        data=category_create,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)


def test_wrong_token(client, category, category_create, session, wrong_token):
    category_id = category.id
    client.cookies = {"token": wrong_token}
    response = client.post(
        url=SETTINGS.urls.update_category.format(category_id=category_id),
        data=category_create,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)
