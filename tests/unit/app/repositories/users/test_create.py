import pytest

from app.exceptions import DuplicateNameCreateError, EmptyStringError
from app.repositories.users import UserRepo
from app.schemas.users import UserCreate
from app.utils.tools.helpers import hash_password
from tests.conftest import clean_db, get_dict_to_create_user, get_users


def test_create_user(session, user):
    user_params = get_dict_to_create_user(user=user, session=session)
    assert not get_users(session)
    UserRepo(session).create(UserCreate(**user_params))
    session.expire_all()
    created_user = get_users(session)[0]
    assert created_user
    assert created_user.username == user_params.get("username")
    assert created_user.password_hash_sum == hash_password(
        user_params.get("password")
    )


def test_create_user_duplicate(session, user):
    user_params = get_dict_to_create_user(user=user, session=session)
    assert not get_users(session)
    UserRepo(session).create(UserCreate(**user_params))
    session.expire_all()
    with pytest.raises(DuplicateNameCreateError):
        UserRepo(session).create(UserCreate(**user_params))


def test_create_user_no_username(session, user):
    user_params = get_dict_to_create_user(user=user, session=session)
    assert not get_users(session)
    user_params["username"] = "  "
    with pytest.raises(EmptyStringError):
        UserRepo(session).create(UserCreate(**user_params))
    assert not get_users(session)


def test_create_user_no_password(session, user):
    user_params = get_dict_to_create_user(session=session, user=user)
    clean_db(session)
    assert not get_users(session)
    user_params["password"] = "  "
    with pytest.raises(EmptyStringError):
        UserRepo(session).create(UserCreate(**user_params))
    assert not get_users(session)
