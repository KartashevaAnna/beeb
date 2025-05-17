from fastapi import status
from sqlalchemy import select

from app.exceptions import DuplicateUsernameError, EmptyStringError
from app.models import User
from app.settings import SETTINGS
from tests.conftest import clean_db, get_users
from tests.conftest_helpers import get_test_user_dict


def test_create_user_template(client):
    """Case: endpoint returns form to create a user."""
    response = client.get(url=SETTINGS.urls.signup)
    assert response.status_code == 200


def test_create(session, client):
    user_params = get_test_user_dict()
    assert not get_users(session)

    response = client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER

    statement = select(User).where(User.username == user_params.get("username"))
    result = session.execute(statement)
    assert result.scalars().one_or_none()
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)


def test_create_duplicate(client, session):
    user_params = get_test_user_dict()
    client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )

    response = client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_text = DuplicateUsernameError(user_params.get("username")).detail
    assert error_text in response.text
    clean_db(session)


def test_create_no_username(client, session):
    user_params = get_test_user_dict()
    del user_params["username"]
    response = client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )
    assert not get_users(session)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_empty_username(client, session):
    user_params = get_test_user_dict()
    empty_username = "  "
    user_params["username"] = empty_username
    response = client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )
    assert not get_users(session)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert EmptyStringError().detail in response.text


def test_create_no_password(client, session):
    user_params = get_test_user_dict()
    del user_params["password"]
    response = client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )
    assert not get_users(session)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_empty_password(client, session):
    user_params = get_test_user_dict()
    empty_password = "     "
    user_params["password"] = empty_password
    response = client.post(
        SETTINGS.urls.signup,
        data={**user_params},
    )
    assert not get_users(session)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert EmptyStringError().detail in response.text
