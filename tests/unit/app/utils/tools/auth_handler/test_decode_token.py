from jose import JWTError
import pytest
from app.exceptions import InvalidTokenError
from app.utils.tools.auth_handler import AuthHandler
from tests.conftest import TEST_USER_ID


def test_decode_token():
    username = "Poblebonk"
    token = AuthHandler().encode_token(username=username, id=TEST_USER_ID)
    decoded_token = AuthHandler().decode_token(token)
    assert username == decoded_token["username"]
    assert "username" in decoded_token
    assert "id" in decoded_token
    assert TEST_USER_ID == decoded_token["id"]
    assert "exp" in decoded_token


def test_wrong_token():
    username = "Poblebonk"
    token = AuthHandler().encode_token(username=username, id=TEST_USER_ID)
    token = token[10:]
    with pytest.raises(InvalidTokenError):
        AuthHandler().decode_token(token)
