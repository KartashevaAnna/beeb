from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID, clean_db


def test_get_current_user_balance(
    session, current_payment, month_ago_payment, year_ago_payment, category
):
    salary = Payment(
        name="зарплата",
        price="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
        is_spending=False,
    )
    session.add(salary)
    session.flush()
    session.commit()

    another_user_salary = Payment(
        name="зарплата",
        price="20000",
        user_id=500,
        category_id=category.id,
        is_spending=False,
    )
    session.add(salary)
    session.flush()
    session.commit()

    spendings = (
        current_payment.price + month_ago_payment.price + year_ago_payment.price
    )
    expected_result = salary.price - spendings
    obtained_result = PaymentRepo(session).get_current_user_balance(
        TEST_USER_ID
    )
    assert expected_result == obtained_result
    clean_db(session)
