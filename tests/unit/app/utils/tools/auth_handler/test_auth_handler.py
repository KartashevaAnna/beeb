import datetime

import pytest

from app.exceptions import ExpiredTokenError
from tests.conftest import TEST_USER_ID


def test_signature_expired(auth_handler):
    stale_token = auth_handler.encode_token(
        username="test_user",
        id=TEST_USER_ID,
        expires_delta=datetime.timedelta(days=-100),
    )
    with pytest.raises(ExpiredTokenError):
        assert auth_handler.decode_token(stale_token)
