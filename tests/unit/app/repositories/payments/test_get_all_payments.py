import datetime

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentCreate
from tests.conftest import (
    TEST_USER_ID,
    check_that_payments_belong_to_test_user,
    clean_db,
)


def test_payment_repo_get_all_payments_for_the_user(
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
    dict_for_new_payment,
):
    dict_for_new_payment["user_id"] = 600
    del dict_for_new_payment["price"]
    del dict_for_new_payment["date"]
    dict_for_new_payment["price_in_rub"] = 400
    dict_for_new_payment["created_at"] = datetime.datetime.now()

    payment = PaymentCreate(**dict_for_new_payment)
    new_payment = Payment(**payment.model_dump())
    session.add(new_payment)
    session.commit()
    result = PaymentRepo(session).get_all_payments(TEST_USER_ID)
    assert year_ago_payment in result
    assert year_ago_payment_later in result
    assert month_ago_payment in result
    assert month_ago_payment_later in result
    assert current_payment in result
    assert year_after_payment in result
    check_that_payments_belong_to_test_user(payments=result)
    clean_db(session)
