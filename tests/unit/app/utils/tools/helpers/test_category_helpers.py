from app.utils.tools.category_helpers import add_category_to_db
from tests.conftest import get_categories


def test_add_category_to_db(session):
    assert not get_categories(session)
    category_name = "специи"
    add_category_to_db(session=session, name=category_name)
    created_category = get_categories(session)[0]
    assert created_category.name == category_name
