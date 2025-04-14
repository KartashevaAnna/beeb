from app.repositories.payments import PaymentRepo
from app.utils.tools.helpers import get_readable_price
from tests.conftest import get_payments


def test_payments_total(fill_db, session):
    """Case: normal mode.

    Checks that the repo return total payments correctly.
    """
    all_payments = get_payments(session)
    total = sum(payment.price for payment in all_payments)
    assert PaymentRepo(session).get_total() == get_readable_price(total)


def test_payments_total_days_no_payments(session):
    """Case: there are no payments in database.

    Check that the repo returns 0.
    """
    assert PaymentRepo(session).get_total_days() == 0


def test_payments_total_days_just_one_payment(session, category):
    """Case: there is only one entry in the database.

    Check that the repo returns 0.
    """
    assert PaymentRepo(session).get_total_days() == 0
