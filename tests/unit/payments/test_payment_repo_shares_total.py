from app.repositories.payments import PaymentRepo


def test_get_monthly_payments_shares_total(client, fill_db, session):
    """Case: normal mode. Verify monthly payments.

    Checks that the helper function called by the repo
    correctly calculates the share of payments per category in overall payments.
    """
    monthly_payments_shares_total = PaymentRepo(
        session
    ).get_total_monthly_payments_shares()
    checksum = int(sum(list(monthly_payments_shares_total.values())))
    assert checksum <= 100
