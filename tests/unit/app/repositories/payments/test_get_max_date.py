import datetime

from app.repositories.payments import PaymentRepo
from app.schemas.dates import DateFilter
from tests.conftest import TEST_USER_ID


def test_payment_repo_get_max_date_no_year_no_month(
    client,
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    limit = DateFilter(year=None, month=None)
    result = PaymentRepo(session).get_max_date(
        limit=limit, user_id=TEST_USER_ID
    )
    assert result.date() == year_after_payment.created_at.date()


def test_payment_repo_get_max_date_year_no_month(
    client,
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    current_year = datetime.datetime.now().date().year
    limit = DateFilter(year=current_year, month=None)
    result = PaymentRepo(session).get_max_date(
        limit=limit, user_id=TEST_USER_ID
    )
    assert result.date() == current_payment.created_at.date()


def test_payment_repo_get_max_date_year_month(
    client,
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    current_year = datetime.datetime.now().date().year
    previous_month = month_ago_payment.created_at.date().month

    limit = DateFilter(year=current_year, month=previous_month)
    result = PaymentRepo(session).get_max_date(
        limit=limit, user_id=TEST_USER_ID
    )
    assert result.date() == month_ago_payment_later.created_at.date()
