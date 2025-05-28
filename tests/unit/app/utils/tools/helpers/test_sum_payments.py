import datetime

from app.utils.tools.helpers import get_monthly_payments
from tests.conftest import add_payment, get_payments


def test_get_monthly_payments(session, category, user):
    """Case: normal mode. Verify monthly payments.

    Checks that the helper function called by the repo
    correctly adds up monthly payments.
    """
    # create three payments: 1 for current month and 2 for the previous month
    first_payment = add_payment(
        user=user,
        session=session,
        amount=100,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    second_payment = add_payment(
        session=session,
        user=user,
        amount=400,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=-8),
    )
    third_payment = add_payment(
        user=user,
        session=session,
        amount=200,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=-8),
    )
    session.commit()
    # get a list of all created payments and pass it to the helper function
    all_payments = get_payments(session)
    # get a response from the helper function adding up payments
    monthly_breakdown = get_monthly_payments(all_payments)
    assert (
        monthly_breakdown[first_payment.created_at.strftime("%m")]
        == first_payment.amount
    )
    assert (
        monthly_breakdown[second_payment.created_at.strftime("%m")]
        == second_payment.amount + third_payment.amount
    )
