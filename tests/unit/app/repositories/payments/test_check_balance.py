from contextlib import nullcontext
import datetime
import pytest
from sqlalchemy import func, select

from app.exceptions import SpendingOverBalanceError
from app.models import Income, Payment
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentCreate
from tests.conftest import TEST_USER_ID, clean_db


def test_valid_data_spending_over_balance(
    session,
    fill_db,
):
    income = (
        session.query(func.sum(Income.amount))
        .where(Income.user_id == TEST_USER_ID)
        .scalar()
    )
    max_date = datetime.datetime.now()
    with pytest.raises(SpendingOverBalanceError):
        PaymentRepo(session).check_balance(
            user_id=TEST_USER_ID,
            desired_payment_amount=income + 1,
            max_date=max_date,
            previous_payment_amount=0,
        )


def test_valid_data_spending_over_balance_previous_amount_above_zero(
    session,
    fill_db,
):
    income = (
        session.query(func.sum(Income.amount))
        .where(Income.user_id == TEST_USER_ID)
        .scalar()
    )
    max_date = datetime.datetime.now()
    with pytest.raises(SpendingOverBalanceError):
        PaymentRepo(session).check_balance(
            user_id=TEST_USER_ID,
            desired_payment_amount=income + 1,
            max_date=max_date,
            previous_payment_amount=500,
        )


def test_valid_data_spending_over_balance_last_month(
    session, current_payment, month_ago_payment, year_ago_payment
):
    max_date = month_ago_payment.created_at
    income = 0

    with pytest.raises(SpendingOverBalanceError):
        PaymentRepo(session).check_balance(
            user_id=TEST_USER_ID,
            desired_payment_amount=income + 1,
            max_date=max_date,
            previous_payment_amount=0,
        )


def test_valid_data_spending_over_balance_last_month_previous_amount_above_zero(
    session, current_payment, month_ago_payment, year_ago_payment
):
    max_date = month_ago_payment.created_at
    income = 0

    with pytest.raises(SpendingOverBalanceError):
        PaymentRepo(session).check_balance(
            user_id=TEST_USER_ID,
            desired_payment_amount=income + 1,
            max_date=max_date,
            previous_payment_amount=500,
        )


def test_valid_data_spending_in_balance_last_month_previous_amount_above_zero(
    session,
    current_payment,
    month_ago_payment,
    year_ago_payment,
    positive_balance,
):
    max_date = month_ago_payment.created_at
    with nullcontext():
        PaymentRepo(session).check_balance(
            user_id=TEST_USER_ID,
            desired_payment_amount=1,
            max_date=max_date,
            previous_payment_amount=500,
        )


def test_valid_data_spending_in_balance_above_previous_amount_last_month_previous_amount_above_zero(
    session,
    current_payment,
    month_ago_payment,
    year_ago_payment,
    positive_balance,
):
    max_date = month_ago_payment.created_at
    with nullcontext():
        PaymentRepo(session).check_balance(
            user_id=TEST_USER_ID,
            desired_payment_amount=600,
            max_date=max_date,
            previous_payment_amount=500,
        )
