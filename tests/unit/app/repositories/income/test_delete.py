from app.models import Income
from app.repositories.income import IncomeRepo
from tests.conftest import TEST_USER_ID


def test_delete(session, income):
    income_id = income.id
    IncomeRepo(session).delete(user_id=TEST_USER_ID, income_id=income_id)
    deleted_income = session.get(Income, income_id)
    assert not deleted_income
