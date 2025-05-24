from app.repositories.payments import PaymentRepo


def test_get_days_left(session):
    result = PaymentRepo(session).get_days_left(
        available_amount=50, rate_per_day=10
    )
    assert result == 5


def test_get_days_left_no_total_per_dat(session):
    result = PaymentRepo(session).get_days_left(available_amount=50)
    assert not result
