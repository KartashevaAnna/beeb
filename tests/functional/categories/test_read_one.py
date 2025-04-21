from unittest.mock import patch

from sqlalchemy import func, select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import payment, raise_always


def test_category_normal_function(client, category):
    """Case: normal mode.

    Checks that the endpoint returns page
    with one payment in context.
    """
    response = client.get(
        SETTINGS.urls.category.format(category_id=category.id)
    )
    assert response.status_code == 200
    assert category.name.title() in response.text


def test_category_404(client, session, fill_db):
    """Case: user request a nonexistant id.

    Checks that the endpoint returns a 404 status code.
    """
    max_category_id = session.scalar(select(func.max(Category.id)))
    non_existing_category_id = max_category_id + 1
    response = client.get(
        SETTINGS.urls.category.format(category_id=non_existing_category_id)
    )
    assert response.status_code == 404


def test_category_empty_db_404(client):
    """Case: the database is empty.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.category.format(category_id=1))
    assert response.status_code == 404


@patch.object(CategoryRepo, "read", raise_always, payment)
def test_category_exception(client):
    """Case: any exception is thrown."""
    response = client.get(SETTINGS.urls.category.format(category_id=1))
    assert response.status_code != 200
