import pytest

from app.exceptions import DuplicateUsernameError, EmptyStringError
from app.repositories.users import UserRepo
from app.schemas.users import UserCreate
from app.utils.tools.helpers import hash_password
from tests.conftest import clean_db, get_users
from tests.conftest_helpers import get_test_user_dict


def test_create_user(session):
    assert not get_users(session)
    user_params = get_test_user_dict()
    UserRepo(session).create(UserCreate(**user_params))
    session.expire_all()
    created_user = get_users(session)[0]
    assert created_user
    assert created_user.username == user_params.get("username")
    assert created_user.password_hash_sum == hash_password(
        user_params.get("password")
    )
    clean_db(session)


def test_create_user_duplicate(session):
    assert not get_users(session)
    user_params = get_test_user_dict()
    UserRepo(session).create(UserCreate(**user_params))
    session.expire_all()
    with pytest.raises(DuplicateUsernameError):
        UserRepo(session).create(UserCreate(**user_params))
    clean_db(session)


def test_create_user_no_username(session):
    assert not get_users(session)
    user_params = get_test_user_dict()
    user_params["username"] = "  "
    with pytest.raises(EmptyStringError):
        UserRepo(session).create(UserCreate(**user_params))
    assert not get_users(session)


def test_create_user_no_password(session):
    assert not get_users(session)
    user_params = get_test_user_dict()
    user_params["password"] = "  "
    with pytest.raises(EmptyStringError):
        UserRepo(session).create(UserCreate(**user_params))
    assert not get_users(session)
