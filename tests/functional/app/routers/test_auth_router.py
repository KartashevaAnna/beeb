import copy
from unittest.mock import patch

from fastapi import status

from app.exceptions import UserNotFoundError, WrongPasswordError
from app.repositories.users import UserRepo
from app.settings import SETTINGS
from app.utils.tools.auth_handler import AuthHandler
from tests.conftest import (
    TEST_USER_NAME,
    TEST_USER_PASSWORD,
    get_user,
    raise_always,
)

TEST_LOGIN_DATA = {"username": TEST_USER_NAME, "password": TEST_USER_PASSWORD}


def test_correct_credentials(client, session):
    response = client.post(
        SETTINGS.urls.login,
        data=TEST_LOGIN_DATA,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.home_page
    assert response.cookies
    token = response.cookies.get("token")
    assert token
    decoded_token = AuthHandler().decode_token(token)
    assert "username" in decoded_token
    user = get_user(session)
    assert decoded_token["username"] == user.username


def test_no_such_login(client):
    wrong_username = "wrong_username"
    WRONG_DATA = copy.deepcopy(TEST_LOGIN_DATA)
    WRONG_DATA["username"] = wrong_username
    response = client.post(
        SETTINGS.urls.login,
        data=WRONG_DATA,
    )
    error = UserNotFoundError(wrong_username)
    assert response.status_code == error.status_code
    assert error.detail in response.text


def test_wrong_password(client):
    wrong_password = "wrong_password"
    WRONG_DATA = copy.deepcopy(TEST_LOGIN_DATA)
    WRONG_DATA["password"] = wrong_password
    response = client.post(
        SETTINGS.urls.login,
        data=WRONG_DATA,
    )
    error = WrongPasswordError(username=TEST_USER_NAME, password=wrong_password)
    assert response.status_code == error.status_code
    assert error.detail in response.text


def test_template(client):
    response = client.get(SETTINGS.urls.login)
    assert response.status_code == 200


@patch.object(UserRepo, "get_by_username", raise_always)
def test_exception(client):
    """Case: function that fetches user from db fails."""
    response = client.post(SETTINGS.urls.login, data=TEST_LOGIN_DATA)
    assert response.status_code == 200
    assert "Ошибка" in response.text


def test_nominal_signup_page_server(client):
    """Case: endpoint returns signup modal."""
    response = client.get(SETTINGS.urls.signup)
    assert response.status_code == 200
