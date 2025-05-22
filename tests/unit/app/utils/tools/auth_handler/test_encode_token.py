from datetime import datetime, timedelta, timezone

from app.settings import SETTINGS
from app.utils.tools.auth_handler import AuthHandler
from tests.conftest import TEST_USER_ID


def test_encode_token():
    username = "Poblebonk"
    token = AuthHandler().encode_token(username=username, id=TEST_USER_ID)
    assert token
    assert username not in token
    created_at = datetime.now(timezone.utc).astimezone() + timedelta(
        seconds=SETTINGS.secrets.session_lifetime
    )
    assert created_at.isoformat() not in token
