import datetime

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentCreate
from tests.conftest import (
    TEST_USER_ID,
    check_that_payments_belong_to_test_user,
    check_that_payments_belong_to_test_user_dict,
)


def test_payment_repo_get_all_payments_for_the_user(
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
    get_dict_for_new_payment,
):
    get_dict_for_new_payment["user_id"] = 600
    del get_dict_for_new_payment["amount"]
    del get_dict_for_new_payment["date"]
    get_dict_for_new_payment["amount_in_rub"] = 400
    get_dict_for_new_payment["created_at"] = datetime.datetime.now()

    payment = PaymentCreate(**get_dict_for_new_payment)
    new_payment = Payment(**payment.model_dump())
    session.add(new_payment)
    session.commit()
    received_payments = PaymentRepo(session).read_all(TEST_USER_ID)
    result = str(received_payments)
    assert year_ago_payment.name in result
    assert year_ago_payment_later.name in result
    assert month_ago_payment.name in result
    assert month_ago_payment_later.name in result
    assert current_payment.name in result
    assert year_after_payment.name in result
    check_that_payments_belong_to_test_user(payments=received_payments)
