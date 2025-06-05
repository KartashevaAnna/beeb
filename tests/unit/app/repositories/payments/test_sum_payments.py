import datetime
from app.models import Payment
from app.repositories.payments import PaymentRepo
from tests.conftest import TEST_USER_ID


def test_sum_no_payments(
    session,
):
    expected_result = 0
    max_date = datetime.datetime.now()
    obtained_result = PaymentRepo(session).sum_payments(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_sum_one_payment(session, category):
    expense = Payment(
        name="зарплата",
        amount="20",
        user_id=TEST_USER_ID,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    session.add(expense)
    session.flush()
    session.commit()
    max_date = datetime.datetime.now()
    expected_result = int(expense.amount)
    obtained_result = PaymentRepo(session).sum_payments(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_sum_two_payments(session, category):
    expense = Payment(
        name="зарплата",
        amount="20",
        user_id=TEST_USER_ID,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    session.add(expense)
    session.flush()
    session.commit()

    second_expense = Payment(
        name="зарплата",
        amount="5",
        user_id=TEST_USER_ID,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    session.add(second_expense)
    session.flush()
    session.commit()
    max_date = datetime.datetime.now()
    expected_result = int(expense.amount) + int(second_expense.amount)
    obtained_result = PaymentRepo(session).sum_payments(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result


def test_sum_two_payments_one_in_the_future(session, category):
    expense = Payment(
        name="зарплата",
        amount="20",
        user_id=TEST_USER_ID,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    session.add(expense)
    session.flush()
    session.commit()

    second_expense = Payment(
        name="зарплата",
        amount="5",
        user_id=TEST_USER_ID,
        category_id=category.id,
        created_at=datetime.datetime.now() + datetime.timedelta(days=5),
    )
    session.add(second_expense)
    session.flush()
    session.commit()
    max_date = datetime.datetime.now()
    expected_result = int(expense.amount)
    obtained_result = PaymentRepo(session).sum_payments(
        user_id=TEST_USER_ID, max_date=max_date
    )
    assert expected_result == obtained_result
