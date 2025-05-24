import datetime

from sqlalchemy import func, select

from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID, add_payment, get_payments


def test_payments_total(fill_db, session):
    """Case: normal mode.

    Checks that the repo return total payments correctly.
    """
    all_payments = get_payments(session)
    total = sum(payment.price for payment in all_payments)
    repo = PaymentRepo(session)
    assert repo.get_total(repo.get_all_payments(user_id=TEST_USER_ID)) == total


def test_payments_total_days_no_payments(session):
    """Case: there are no payments in database.

    Check that the repo returns 0.
    """
    max_date = session.scalar(select(func.max(Payment.created_at)))
    min_date = session.scalar(select(func.min(Payment.created_at)))
    assert PaymentRepo(session).get_total_days(max_date, min_date) == 0


def test_payments_total_days_just_one_payment(session, payment):
    """Case: there is only one entry in the database.

    Check that the repo returns 0.
    """
    max_date = None
    min_date = None
    assert PaymentRepo(session).get_total_days(max_date, min_date) == 0


def test_payments_total_days_delta_two_days(session, category, fill_db, user):
    category_id = category.id
    created_at_now = datetime.datetime.now()
    created_at_two_days_before = datetime.datetime.now() - datetime.timedelta(
        days=2
    )
    first_payment = add_payment(
        user=user,
        session=session,
        category_id=category_id,
        created_at=created_at_now,
        price=40,
    )
    second_payment = add_payment(
        user=user,
        session=session,
        category_id=category_id,
        created_at=created_at_two_days_before,
        price=40,
    )
    max_date = first_payment.created_at
    min_date = second_payment.created_at
    assert PaymentRepo(session).get_total_days(max_date, min_date) == 2


def test_get_payments_per_year(session, fill_db):
    year = datetime.datetime.now().year
    payments = PaymentRepo(session).get_payments_per_year(
        year, user_id=TEST_USER_ID
    )
    assert len(payments) == len(get_payments(session))


def test_get_payments_per_year_no_entries_previous_year(session, fill_db):
    year = datetime.datetime.now().year - 1
    payments = PaymentRepo(session).get_payments_per_year(
        year, user_id=TEST_USER_ID
    )
    assert not payments


def test_get_payments_per_year_empty_db(session):
    year = datetime.datetime.now().year
    payments = PaymentRepo(session).get_payments_per_year(
        year, user_id=TEST_USER_ID
    )
    assert not payments


def test_get_payments_per_year_one_in_previous_year(
    session, category, fill_db, user
):
    category_id = category.id
    year = datetime.datetime.now().year - 1
    created_at = datetime.datetime.now() - datetime.timedelta(weeks=52)
    add_payment(
        user=user,
        session=session,
        category_id=category_id,
        created_at=created_at,
        price=40,
    )
    payments = PaymentRepo(session).get_payments_per_year(
        year, user_id=TEST_USER_ID
    )
    assert len(payments) == 1
    assert payments[0].created_at.year == year


def test_sum_payments_prices(session, fill_db):
    payments = get_payments(session)
    repo_sum = PaymentRepo(session).sum_payments_prices(payments)
    checksum = sum(payment.price for payment in payments)
    assert repo_sum == checksum


def test_get_payments_per_year_with_category_one_in_previous_year(
    session, category, fill_db, user
):
    category_id = category.id
    year = datetime.datetime.now().year - 1
    created_at = datetime.datetime.now() - datetime.timedelta(weeks=52)
    add_payment(
        user=user,
        session=session,
        category_id=category_id,
        created_at=created_at,
        price=40,
    )
    payments = PaymentRepo(session).get_payments_per_year_with_category(
        year, user_id=TEST_USER_ID
    )
    assert len(payments) == 1
    assert payments[0].created_at.year == year


def test_get_rate_per_day(session, category, fill_db, user):
    category_id = category.id
    created_at = datetime.datetime.now() - datetime.timedelta(weeks=2)
    add_payment(
        user=user,
        session=session,
        category_id=category_id,
        created_at=created_at,
        price=40,
    )
    max_date = session.scalar(select(func.max(Payment.created_at)))
    min_date = session.scalar(select(func.min(Payment.created_at)))
    total_days = max_date - min_date
    total_days = int(total_days.days)
    statement = select(func.sum(Payment.price))
    results = session.execute(statement)
    total = results.fetchall()[0][0]
    computed = PaymentRepo(session).get_rate_per_day(
        expenses=total, elapsed_days=total_days
    )
    assert round(round(computed, 2) * total_days) == total


def test_get_rate_per_day_zerodivision_error(session):
    total = 500
    total_days = 0
    computed = PaymentRepo(session).get_rate_per_day(
        expenses=total, elapsed_days=total_days
    )
    assert computed == total
