import datetime
import pytest
from sqlalchemy import func, select
from app.exceptions import SpendingOverBalanceError
from app.models import Income, Payment
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentCreate
from tests.conftest import clean_db


def test_valid_data_spending_over_balance(
    session, fill_db, create_payment_food
):
    max_id_before = session.scalar(select(func.max(Payment.id)))
    previous_payment = session.get(Payment, max_id_before)
    income = (
        session.query(func.sum(Income.amount))
        .where(Income.user_id == previous_payment.user_id)
        .scalar()
    )
    create_payment_food["amount_in_rub"] = income + 5000
    create_payment_food["created_at"] = datetime.datetime.now()
    with pytest.raises(SpendingOverBalanceError):
        PaymentRepo(session).create(
            PaymentCreate(**create_payment_food),
            user_id=previous_payment.user_id,
        )
    max_id_after = session.scalar(select(func.max(Payment.id)))
    assert max_id_before == max_id_after
