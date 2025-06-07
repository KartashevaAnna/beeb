from copy import deepcopy
import datetime

import pytest

from app.exceptions import NotOwnerError, SpendingOverBalanceError
from app.models import Income, Payment
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentUpdate
from tests.conftest import TEST_USER_ID


def test_not_owner(update_payment_repo, session, positive_balance):
    payment_update_local = deepcopy(update_payment_repo)
    payment_update_local["user_id"] = str(500)
    update = PaymentUpdate(**payment_update_local)
    with pytest.raises(NotOwnerError):
        PaymentRepo(session).update(
            payment_id=payment_update_local["id"], to_update=update
        )


def test_spending_over_balance(update_payment_repo, session):
    update = PaymentUpdate(**update_payment_repo)
    with pytest.raises(SpendingOverBalanceError):
        PaymentRepo(session).update(
            payment_id=update_payment_repo["id"], to_update=update
        )


def test_update_amount(update_payment_repo, session, positive_balance):
    payment_update_local = deepcopy(update_payment_repo)
    new_amount = "75"
    payment_update_local["amount"] = new_amount
    update = PaymentUpdate(**payment_update_local)
    PaymentRepo(session).update(
        payment_id=payment_update_local["id"], to_update=update
    )
    updated_payment = session.get(Payment, payment_update_local["id"])
    assert updated_payment.amount == int(new_amount) * 100


def test_update_name(update_payment_repo, session, positive_balance):
    payment_update_local = deepcopy(update_payment_repo)
    new_name = "Balrog"
    payment_update_local["name"] = new_name

    update = PaymentUpdate(**payment_update_local)
    PaymentRepo(session).update(
        payment_id=payment_update_local["id"], to_update=update
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment_update_local["id"])
    assert updated_payment.name == new_name.lower()


def test_update_category_id(update_payment_repo, session, positive_balance):
    payment_update_local = deepcopy(update_payment_repo)
    payment_update_local["category_id"] = update_payment_repo["category_id"] + 1
    update = PaymentUpdate(**payment_update_local)
    PaymentRepo(session).update(
        payment_id=payment_update_local["id"], to_update=update
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment_update_local["id"])
    assert updated_payment.category_id == update_payment_repo["category_id"] + 1


def test_update_grams(update_payment_repo, session, positive_balance):
    payment_update_local = deepcopy(update_payment_repo)
    payment_update_local["grams"] = 600
    update = PaymentUpdate(**payment_update_local)
    PaymentRepo(session).update(
        payment_id=payment_update_local["id"], to_update=update
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment_update_local["id"])
    assert updated_payment.grams == 600


def test_update_quantity(update_payment_repo, session, positive_balance):
    payment_update_local = deepcopy(update_payment_repo)
    payment_update_local["quantity"] = 60
    update = PaymentUpdate(**payment_update_local)
    PaymentRepo(session).update(
        payment_id=payment_update_local["id"], to_update=update
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment_update_local["id"])
    assert updated_payment.quantity == 60
