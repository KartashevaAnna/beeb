from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID


def test_get_monthly_payments_shares_total(fill_db, session):
    """Case: normal mode. Verify monthly payments.

    Checks that the helper function called by the repo
    correctly calculates the share
    of payments per category in overall payments.
    """
    repo = PaymentRepo(session)
    monthly_payments_shares_total = repo.get_total_monthly_payments_shares(
        repo.read_all(TEST_USER_ID)
    )
    checksum = int(sum(monthly_payments_shares_total.keys()))
    assert checksum <= 100
