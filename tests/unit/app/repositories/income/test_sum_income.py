import datetime
from app.models import Income
from app.repositories.income import IncomeRepo
from tests.conftest import TEST_USER_ID


def test_sum_no_salary(
    session,
):
    expected_result = 0
    max_date = datetime.datetime.now().astimezone()
    obtained_result = IncomeRepo(session).sum_income(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_sum_one_salary(
    session,
):
    salary = Income(
        name="зарплата",
        amount="20",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()
    expected_result = int(salary.amount)
    max_date = datetime.datetime.now().astimezone()

    obtained_result = IncomeRepo(session).sum_income(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_sum_two_salaries(
    session,
):
    salary = Income(
        name="зарплата",
        amount="20",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()

    second_salary = Income(
        name="зарплата",
        amount="5",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(second_salary)
    session.flush()
    session.commit()
    expected_result = int(salary.amount) + int(second_salary.amount)
    max_date = datetime.datetime.now().astimezone()
    obtained_result = IncomeRepo(session).sum_income(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_sum_two_salaries_one_in_the_future(
    session,
):
    salary = Income(
        name="зарплата",
        amount="20",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()

    second_salary = Income(
        name="зарплата",
        amount="5",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now() + datetime.timedelta(days=5),
    )
    session.add(second_salary)
    session.flush()
    session.commit()
    expected_result = int(salary.amount)
    max_date = datetime.datetime.now().astimezone()
    obtained_result = IncomeRepo(session).sum_income(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result
