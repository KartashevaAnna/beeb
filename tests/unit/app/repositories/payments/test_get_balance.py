import datetime
from app.models import Income
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID


def test_get_balance(
    session, current_payment, month_ago_payment, year_ago_payment
):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()
    spendings = (
        current_payment.amount
        + month_ago_payment.amount
        + year_ago_payment.amount
    )
    max_date = datetime.datetime.now()
    expected_result = salary.amount - spendings
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_month_ago_payment_month_ago_income(
    session, current_payment, month_ago_payment, year_ago_payment
):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=month_ago_payment.created_at,
    )
    session.add(salary)
    session.flush()
    session.commit()
    spendings = +month_ago_payment.amount + year_ago_payment.amount
    max_date = month_ago_payment.created_at
    expected_result = salary.amount - spendings
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_month_ago_payment_current_income(
    session, current_payment, month_ago_payment, year_ago_payment
):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()
    spendings = month_ago_payment.amount + year_ago_payment.amount
    max_date = month_ago_payment.created_at
    expected_result = -spendings
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_no_salary(
    session,
    current_payment,
    month_ago_payment,
    year_ago_payment,
):
    spendings = (
        current_payment.amount
        + month_ago_payment.amount
        + year_ago_payment.amount
    )
    max_date = datetime.datetime.now()
    expected_result = -spendings
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_only_salary_outside_of_requested_period(session):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()
    max_date = datetime.datetime.now() - datetime.timedelta(weeks=3)
    expected_result = 0
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_only_salary(session):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()
    max_date = datetime.datetime.now()
    expected_result = salary.amount
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_only_salary_in_the_past(session):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now() - datetime.timedelta(days=50),
    )
    session.add(salary)
    session.flush()
    session.commit()
    max_date = salary.created_at
    expected_result = salary.amount
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_two_salaries(
    session,
):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(salary)
    session.flush()
    session.commit()

    second_salary = Income(
        name="зарплата",
        amount="5000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(second_salary)
    session.flush()
    session.commit()
    max_date = datetime.datetime.now()
    expected_result = int(salary.amount) + int(second_salary.amount)
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_get_balance_two_salaries_one_in_the_past(
    session,
):
    salary = Income(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now() - datetime.timedelta(days=3),
    )
    session.add(salary)
    session.flush()
    session.commit()

    second_salary = Income(
        name="зарплата",
        amount="5000",
        user_id=TEST_USER_ID,
        created_at=datetime.datetime.now(),
    )
    session.add(second_salary)
    session.flush()
    session.commit()
    max_date = salary.created_at
    expected_result = int(salary.amount)
    obtained_result = PaymentRepo(session).get_balance(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result
