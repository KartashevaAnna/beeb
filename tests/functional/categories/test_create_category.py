from unittest.mock import patch

from sqlalchemy import select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import clean_db, raise_always

NAME = "древесина"


def test_create_category_template(client):
    """Case: endpoint returns form to create a category."""
    response = client.get(url=SETTINGS.urls.create_category)
    assert response.status_code == 200
    assert "название" in response.text


def test_create_category_valid_data(session, client):
    """Case: endpoint creates a category in db on valid request."""

    response = client.post(
        url=SETTINGS.urls.create_category,
        data={
            "name": NAME,
        },
    )
    assert response.status_code == 303

    statement = select(Category).where(Category.name == NAME)
    results = session.execute(statement)
    category = results.scalars().one_or_none()
    assert category
    assert response.headers.get("location") == SETTINGS.urls.create_category
    clean_db(session)


def test_create_category_invalid_name(client):
    """Case: endpoint fails creating a category in db with invalid request."""

    response = client.post(
        url=SETTINGS.urls.create_category,
        data={
            "name": None,
        },
    )
    assert response.status_code == 422


def test_create_category_invalid_data(client):
    """Case: endpoint fails creating a category in db with invalid request."""

    response = client.post(
        url=SETTINGS.urls.create_category,
        data={
            "unexpected_parameter": "hello_world",
        },
    )
    assert response.status_code == 422


def test_create_duplicate_category(client, category):
    """Case: endpoint refuses creating a category with a duplicate name."""

    response = client.post(
        url=SETTINGS.urls.create_category,
        data={
            "name": category.name,
        },
    )
    assert response.status_code == 406


@patch.object(
    CategoryRepo,
    "create",
    raise_always,
)
def test_create_category_any_other_exception(client):
    """Case: endpoint returns 501.

    Covers any exception other than HTTPException with 406 error code
    or 422 Unprocessable entity.
    """
    response = client.post(
        url=SETTINGS.urls.create_category,
        data={
            "name": NAME,
        },
    )
    assert response.status_code == 501
