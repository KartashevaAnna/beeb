from app.repositories.users import UserRepo
from tests.conftest import clean_db


def test_get_by_username(user, session):
    found_user = UserRepo(session).get_by_username(user.username)
    assert user == found_user
    clean_db(session)
