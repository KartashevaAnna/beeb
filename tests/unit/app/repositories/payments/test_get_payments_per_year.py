from app.repositories.payments import PaymentRepo


def test_payment_repo_get_payments_per_year(
    client,
    session,
    year_after_payment,
    year_ago_payment,
    year_ago_payment_later,
    month_ago_payment,
    month_ago_payment_later,
    current_payment,
):
    year = year_ago_payment.created_at.date().year
    result = PaymentRepo(session).get_payments_per_year(year=year)
    assert year_ago_payment in result
    assert year_ago_payment_later in result
    assert month_ago_payment not in result
    assert month_ago_payment_later not in result
    assert current_payment not in result
    assert year_after_payment not in result
