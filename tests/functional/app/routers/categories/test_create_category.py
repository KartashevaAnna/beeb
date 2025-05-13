from copy import copy
from unittest.mock import patch

from sqlalchemy import select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import CATEGORY_NAME, clean_db, raise_always


def test_create_category_template(client):
    """Case: endpoint returns form to create a category."""
    response = client.get(url=SETTINGS.urls.create_category)
    assert response.status_code == 200
    assert "название" in response.text


def test_create_category_valid_data(session, client, category_create):
    """Case: endpoint creates a category in db on valid request."""

    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == 303

    statement = select(Category).where(Category.name == CATEGORY_NAME)
    results = session.execute(statement)
    category = results.scalars().one_or_none()
    assert category
    assert response.headers.get("location") == SETTINGS.urls.create_category
    clean_db(session)


def test_create_category_invalid_name(client, category_create):
    """Case: endpoint fails creating a category in db with invalid request."""
    category_create = copy(category_create)
    category_create["name"] = None
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == 422


def test_create_category_invalid_data(client, category_create):
    """Case: endpoint fails creating a category in db with invalid request."""
    category_create = copy(category_create)
    category_create.pop("name", None)
    category_create["unexpected_parameter"] = "hello_world"
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == 422


def test_create_duplicate_category(client, category, category_create):
    """Case: endpoint refuses creating a category with a duplicate name."""
    category_create = copy(category_create)
    category_create["name"] = category.name
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == 406


@patch.object(
    CategoryRepo,
    "create",
    raise_always,
)
def test_create_category_any_other_exception(client, category_create):
    """Case: endpoint returns 501.

    Covers any exception other than HTTPException with 406 error code
    or 422 Unprocessable entity.
    """
    response = client.post(
        url=SETTINGS.urls.create_category, data=category_create
    )
    assert response.status_code == 501
