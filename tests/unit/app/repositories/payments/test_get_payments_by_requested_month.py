from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID, clean_db


def test_normal_function(
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
    all_spendings = [month_ago_payment, year_ago_payment]
    month = month_ago_payment.created_at.month + 1
    year = month_ago_payment.created_at.year
    obtained_result = PaymentRepo(session).get_payments_by_requested_month(
        user_id=TEST_USER_ID, month=month, year=year
    )
    all_spendings = [(x.name, x.created_at) for x in all_spendings]
    obtained_result = [(x.name, x.created_at) for x in obtained_result]
    assert all_spendings == obtained_result
    clean_db(session)
