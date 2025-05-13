from app.repositories.payments import PaymentRepo


def test_payment_repo_get_all_payments(
    client,
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    result = PaymentRepo(session).get_all_payments()
    assert year_ago_payment in result
    assert year_ago_payment_later in result
    assert month_ago_payment in result
    assert month_ago_payment_later in result
    assert current_payment in result
    assert year_after_payment in result
