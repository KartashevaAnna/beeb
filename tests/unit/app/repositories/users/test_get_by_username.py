from app.repositories.users import UserRepo
from tests.conftest import clean_db, get_user


def test_get_by_username(user, session):
    user = get_user(session)
    found_user = UserRepo(session).get_by_username(user.username)
    assert user == found_user
    clean_db(session)
