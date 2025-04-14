from unittest.mock import patch

from sqlalchemy import select

from app.models import Category
from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS
from tests.conftest import raise_always


def test_categories_normal_function(client, fill_db, session):
    """Case: normal mode.

    Checks that the endpoint returns page
    with categories in context.
    """
    response = client.get(SETTINGS.urls.categories)
    assert response.status_code == 200
    all_categories = session.scalars(select(Category)).all()
    assert len(all_categories) > 2
    category = all_categories[2]
    assert category.name.title() in response.text


def test_categories_empty_db(client):
    """Case: the database is empty.

    Checks that the endpoint returns page
    with no categories in context.
    """
    response = client.get(SETTINGS.urls.categories)
    assert response.status_code == 200
    assert response.context["categories"] == []


@patch.object(CategoryRepo, "read_all", raise_always)
def test_payments_exception(client):
    """Case: any exception is thrown.

    Checks that the endpoint returns an error page.
    """
    response = client.get(SETTINGS.urls.categories)
    assert response.status_code != 200
    assert "exception" in response.text
