import pytest

from app.exceptions import DuplicateEmailError
from app.repositories.users import UserRepo
from app.utils.tools.helpers import hash_password
from tests.conftest import clean_db, get_users
from tests.conftest_helpers import get_test_user_dict


def test_create_user(session):
    assert not get_users(session)
    test_user_params = get_test_user_dict()
    UserRepo(session).create(**test_user_params)
    session.expire_all()
    created_user = get_users(session)[0]
    assert created_user
    assert created_user.email == test_user_params.get("email")
    assert created_user.password_hash_sum == hash_password(
        test_user_params.get("password")
    )
    assert created_user.first_name == test_user_params.get("first_name")
    assert created_user.last_name == test_user_params.get("last_name")
    clean_db(session)


def test_create_user_duplicate(session):
    assert not get_users(session)
    user_params = get_test_user_dict()
    UserRepo(session).create(**user_params)
    session.expire_all()
    with pytest.raises(DuplicateEmailError):
        UserRepo(session).create(**user_params)

    clean_db(session)
