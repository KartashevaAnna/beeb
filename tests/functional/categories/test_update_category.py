from unittest.mock import patch

from fastapi import status

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import get_categories, raise_always

NAME = "exotic_category"


def test_serve_template_update_category(client, category):
    """Case: endpoint returns form to update a category."""
    category_id = category.id
    response = client.get(
        SETTINGS.urls.update_category.format(category_id=category_id)
    )
    assert response.status_code == 200
    assert category.name.title() in response.text


def test_update__category_name(client, category, session):
    """Case: endpoint updates a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": NAME, "is_active": category.is_active},
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.categories
    session.expire_all()
    updated_category = session.get(Category, category_id)
    assert category_id == updated_category.id
    assert updated_category.name == NAME
    assert updated_category.is_active == category.is_active


def test_update__category_change_status(client, category):
    """Case: endpoint updates a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={
            "name": category.name,
            "is_active": False,
        },
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER


def test_update__category_duplicate_name(client, categories, session):
    """Case: endpoint refuses updating a category."""
    categories = get_categories(session)
    category_id = categories[0].id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={
            "name": categories[1].name,
            "is_active": categories[0].is_active,
        },
    )
    assert response.status_code == status.HTTP_304_NOT_MODIFIED


def test_update__category_name_is_None(client, category):
    """Case: endpoint refuses updating a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": None, "is_active": category.is_active},
    )
    assert response.status_code == 422


def test_update_category_serve_template_404(client):
    """Case: user requests update of a nonexistant category.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.update_category.format(category_id=1))
    assert response.status_code == 404


@patch.object(CategoryRepo, "update", raise_always)
def test_update_payment_exception(client, category):
    """Case: any exception is thrown."""
    category_id = category.id
    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": NAME, "is_active": category.is_active},
    )
    assert response.status_code == 501
    assert "exception" in response.text
