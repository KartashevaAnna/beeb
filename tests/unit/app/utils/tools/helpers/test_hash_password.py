from app.utils.tools.helpers import hash_password
from tests.conftest import TEST_PASSWORD


def test_hash_password():
    first_hash = hash_password(TEST_PASSWORD)
    second_hash = hash_password(TEST_PASSWORD)
    assert first_hash == second_hash
