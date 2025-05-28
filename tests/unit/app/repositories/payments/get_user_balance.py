from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID, clean_db


def test_get_user_balance(
    session, current_payment, month_ago_payment, year_ago_payment, category
):
    salary = Payment(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
        is_spending=False,
    )
    session.add(salary)
    session.flush()
    session.commit()

    another_user_salary = Payment(
        name="зарплата",
        amount="20000",
        user_id=500,
        category_id=category.id,
        is_spending=False,
    )
    session.add(salary)
    session.flush()
    session.commit()

    spendings = (
        int(current_payment.amount)
        + int(month_ago_payment.amount)
        + int(year_ago_payment.amount)
    )
    expected_result = salary.amount - spendings
    obtained_result = PaymentRepo(session).get_user_balance(TEST_USER_ID)
    assert expected_result == obtained_result
    clean_db(session)


def test_get_user_balance_month_ago(
    session, current_payment, month_ago_payment, year_ago_payment, category
):
    # salary = Payment(
    #     name="зарплата",
    #     amount="20000",
    #     user_id=TEST_USER_ID,
    #     category_id=category.id,
    #     is_spending=False,
    # )
    # session.add(salary)
    # session.flush()
    # session.commit()
    all_spendings = [month_ago_payment, current_payment, year_ago_payment]
    spendings = [
        x.amount
        for x in all_spendings
        if x.created_at <= month_ago_payment.created_at
    ]

    expected_result = -sum(spendings)
    month = month_ago_payment.created_at.month
    year = month_ago_payment.created_at.year
    obtained_result = PaymentRepo(session).get_user_balance(
        TEST_USER_ID, month=month, year=year
    )
    assert expected_result == obtained_result
    clean_db(session)
