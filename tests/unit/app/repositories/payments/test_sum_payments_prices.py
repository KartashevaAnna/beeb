from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID


def test_sum_payment_prices(session, category):
    first_payment = Payment(
        name="зарплата",
        price="20000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(first_payment)
    session.flush()
    session.commit()

    second_payment = Payment(
        name="зарплата",
        price="5000",
        user_id=TEST_USER_ID,
        category_id=category.id,
    )
    session.add(second_payment)
    session.flush()
    session.commit()

    expected_result = int(first_payment.price) + int(second_payment.price)
    payments = [first_payment, second_payment]
    obtained_result = PaymentRepo(session).sum_payments_prices(payments)
    assert expected_result == obtained_result
