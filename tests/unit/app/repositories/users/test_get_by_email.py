from app.repositories.users import UserRepo
from tests.conftest import clean_db


def test_get_by_email(user, session):
    found_user = UserRepo(session).get_by_email(user.email)
    assert user == found_user
    clean_db(session)
