from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID


def test_get_balance(
    session, current_payment, month_ago_payment, year_ago_payment, category
):
    salary = Payment(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(salary)
    session.flush()
    session.commit()
    spendings = (
        current_payment.amount
        + month_ago_payment.amount
        + year_ago_payment.amount
    )
    expected_result = salary.amount - spendings
    payments = [salary, current_payment, month_ago_payment, year_ago_payment]
    obtained_result = PaymentRepo(session).get_balance(payments)["balance"]
    assert expected_result == obtained_result


def test_get_balance_no_salary(
    session, current_payment, month_ago_payment, year_ago_payment, category
):
    spendings = (
        current_payment.amount
        + month_ago_payment.amount
        + year_ago_payment.amount
    )
    expected_result = -spendings
    payments = [current_payment, month_ago_payment, year_ago_payment]
    obtained_result = PaymentRepo(session).get_balance(payments)["balance"]
    assert expected_result == obtained_result


def test_get_balance_only_salary(session, category):
    salary = Payment(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(salary)
    session.flush()
    session.commit()

    expected_result = salary.amount
    payments = [salary]
    obtained_result = PaymentRepo(session).get_balance(payments)["balance"]
    assert expected_result == obtained_result


def test_get_balance_two_salaries(
    session,
    category,
    current_payment,
    month_ago_payment,
    year_ago_payment,
):
    salary = Payment(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(salary)
    session.flush()
    session.commit()

    second_salary = Payment(
        name="зарплата",
        amount="5000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(salary)
    session.flush()
    session.commit()

    income = int(salary.amount) + int(second_salary.amount)
    spendings = (
        current_payment.amount
        + month_ago_payment.amount
        + year_ago_payment.amount
    )
    expected_result = income - spendings

    payments = [
        salary,
        second_salary,
        current_payment,
        month_ago_payment,
        year_ago_payment,
    ]
    obtained_result = PaymentRepo(session).get_balance(payments)["balance"]
    assert expected_result == obtained_result
