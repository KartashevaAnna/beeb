from app.utils.tools.helpers import hash_password, is_same_password
from tests.conftest import TEST_PASSWORD


def test_is_same_password():
    password_check_result = is_same_password(
        TEST_PASSWORD, hash_password(TEST_PASSWORD)
    )
    assert password_check_result is True
