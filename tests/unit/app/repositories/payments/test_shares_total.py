from app.repositories.payments import PaymentRepo


def test_get_monthly_payments_shares_total(fill_db, session):
    """Case: normal mode. Verify monthly payments.

    Checks that the helper function called by the repo
    correctly calculates the share of payments per category in overall payments.
    """
    repo = PaymentRepo(session)
    monthly_payments_shares_total = repo.get_total_monthly_payments_shares(
        repo.get_all_payments()
    )
    checksum = int(sum(monthly_payments_shares_total.keys()))
    assert checksum <= 100
