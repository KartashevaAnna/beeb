from copy import copy

import pytest

from app.exceptions import NotOwnerError
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentUpdate


def test_not_owner(update_payment, category, session):
    payment_update_local = copy(update_payment)
    payment_update_local.pop("category", None)
    payment_update_local.pop("form_disabled", None)
    payment_update_local["category_id"] = category.id
    payment_update_local["user_id"] = str(500)
    payment_update_local["amount"] = str(payment_update_local["amount"])
    update = PaymentUpdate(**payment_update_local)
    with pytest.raises(NotOwnerError):
        PaymentRepo(session).update(
            payment_id=payment_update_local["id"], to_update=update
        )
