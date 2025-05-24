from app.utils.tools.helpers import add_payments_to_db
from tests.conftest import (TEST_USER_ID,
                            check_that_payments_belong_to_test_user,
                            get_payments)


def test_add_payments_to_db(session, category):
    """Check that the helper populates the database with payments."""
    # check that there are no payments in the database
    all_payments = get_payments(session)
    assert not all_payments
    # get a response from the helper function adding payments to the database
    add_payments_to_db(session, category_id=category.id, user_id=TEST_USER_ID)
    session.expire_all()
    # verify that payments appered in the database
    all_payments = get_payments(session)
    assert all_payments
    assert len(all_payments) == 1
    check_that_payments_belong_to_test_user(payments=all_payments)
