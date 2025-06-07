import datetime
from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentCreate
from app.utils.tools.helpers import (
    get_max_date_from_year_and_month_datetime_format,
)
from tests.conftest import TEST_USER_ID, check_that_payments_belong_to_test_user


def test_normal_function(
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
    all_spendings = [month_ago_payment, year_ago_payment]
    max_date = month_ago_payment.created_at
    min_date = year_ago_payment.created_at
    obtained_result = PaymentRepo(session).read_all_between_dates(
        user_id=TEST_USER_ID, max_date=max_date, min_date=min_date
    )
    all_spendings = [(x.name, x.created_at) for x in all_spendings]
    obtained_result = [(x.name, x.created_at) for x in obtained_result]
    assert all_spendings == obtained_result


def test_normal_function_for_the_user(
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
    max_date = datetime.datetime.now().astimezone()
    min_date = year_ago_payment.created_at
    received_payments = PaymentRepo(session).read_all_between_dates(
        user_id=TEST_USER_ID, max_date=max_date, min_date=min_date
    )
    result = str(received_payments)
    assert str(year_ago_payment.uuid) in result
    assert str(year_ago_payment_later.uuid) in result
    assert str(month_ago_payment.uuid) in result
    assert str(month_ago_payment_later.uuid) in result
    assert str(current_payment.uuid) in result
    assert str(year_after_payment.uuid) not in result
    check_that_payments_belong_to_test_user(payments=received_payments)


def test_payment_repo_get_payments_per_year_last_year(
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    max_date = get_max_date_from_year_and_month_datetime_format(
        year=year_ago_payment_later.created_at.year,
        month=year_ago_payment_later.created_at.month,
    )
    min_date = year_ago_payment.created_at
    result = PaymentRepo(session).read_all_between_dates(
        user_id=TEST_USER_ID, max_date=max_date, min_date=min_date
    )
    result_names = [x.name for x in result]
    assert year_ago_payment.name in result_names
    assert year_ago_payment_later.name in result_names
    assert month_ago_payment.name not in result_names
    assert month_ago_payment_later.name not in result_names
    assert current_payment.name not in result_names
    assert year_after_payment.name not in result_names


def test_payment_repo_get_payments_per_year_this_year(
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    max_date = get_max_date_from_year_and_month_datetime_format(
        year=month_ago_payment.created_at.year,
        month=12,
    )
    min_date = month_ago_payment.created_at
    result = PaymentRepo(session).read_all_between_dates(
        user_id=TEST_USER_ID, max_date=max_date, min_date=min_date
    )
    result_names = [x.name for x in result]
    assert year_ago_payment.name not in result_names
    assert year_ago_payment_later.name not in result_names
    assert month_ago_payment.name in result_names
    assert month_ago_payment_later.name in result_names
    assert current_payment.name in result_names
    assert year_after_payment.name not in result_names
