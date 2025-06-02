import pytest

from app.exceptions import DuplicateNameCreateError
from app.repositories.categories import CategoryRepo
from app.schemas.categories import CategoryCreate


def test_create_same_name_same_user(session, category_create):
    to_create = CategoryCreate(**category_create)
    with pytest.raises(DuplicateNameCreateError):
        CategoryRepo(session).create(to_create)


def test_create_same_name_different_user(session, category_create):
    to_create = CategoryCreate(**category_create)
    to_create.user_id = 500
    new_category = CategoryRepo(session).create(to_create)
    assert new_category.id
