from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID


def test_sum_payment_amounts(session, category):
    first_payment = Payment(
        name="зарплата",
        amount="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(first_payment)
    session.flush()
    session.commit()

    second_payment = Payment(
        name="зарплата",
        amount="5000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(second_payment)
    session.flush()
    session.commit()

    expected_result = int(first_payment.amount) + int(second_payment.amount)
    payments = [first_payment, second_payment]
    obtained_result = PaymentRepo(session).sum_payment_amounts(payments)
    assert expected_result == obtained_result
