from unittest.mock import patch

from fastapi import status

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import raise_always

NAME = "exotic_category"


def test_serve_template_update_expense(client, category):
    """Case: endpoint returns form to update an expense."""
    category_id = category.id
    response = client.get(
        SETTINGS.urls.update_category.format(category_id=category_id)
    )
    assert response.status_code == 200
    assert category.name.title() in response.text
    assert category.status in response.text


def test_update__category_name(client, category, session):
    """Case: endpoint updates a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": NAME, "category_status": category.status},
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.categories
    session.expire_all()
    updated_category = session.get(Category, category_id)
    assert category_id == updated_category.id
    assert updated_category.name == NAME
    assert updated_category.status == category.status


def test_update__category_duplicate_name(client, category):
    """Case: endpoint refuses updating a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": category.name, "category_status": category.status},
    )
    assert response.status_code == status.HTTP_304_NOT_MODIFIED


def test_update__category_name_is_None(client, category):
    """Case: endpoint refuses updating a category."""
    category_id = category.id

    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": None, "category_status": category.status},
    )
    assert response.status_code == 422


def test_update_category_serve_template_404(client):
    """Case: user requests update of a nonexistant category.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.update_category.format(category_id=1))
    assert response.status_code == 404


@patch.object(CategoryRepo, "update", raise_always)
def test_update_expense_exception(client, category):
    """Case: any exception is thrown."""
    category_id = category.id
    response = client.post(
        SETTINGS.urls.update_category.format(category_id=category_id),
        data={"name": NAME, "category_status": category.status},
    )
    assert response.status_code == 501
    assert "exception" in response.text
