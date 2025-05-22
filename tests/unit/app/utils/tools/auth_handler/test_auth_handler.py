import pytest

from app.exceptions import ExpiredTokenError


def test_signature_expired(auth_handler, stale_token):
    with pytest.raises(ExpiredTokenError):
        assert auth_handler.decode_token(stale_token)
