from copy import copy

import pytest

from app.exceptions import (
    NotIntegerError,
    NotPositiveValueError,
    ValueTooLargeError,
)
from app.schemas.payments import PaymentCreate


def test_add_payment_schema_negative_amount(get_dict_for_new_payment):
    negative_amount = -100
    new_payment = copy(get_dict_for_new_payment)
    new_payment["amount_in_rub"] = negative_amount
    with pytest.raises(NotPositiveValueError) as excinfo:
        PaymentCreate(**new_payment)
    assert str(negative_amount) == str(excinfo.value)


def test_add_payment_schema_amount_not_int(get_dict_for_new_payment):
    not_int_amount = "-100 ₽"
    new_payment = copy(get_dict_for_new_payment)
    new_payment["amount_in_rub"] = not_int_amount

    with pytest.raises(NotIntegerError) as excinfo:
        PaymentCreate(**new_payment)
    assert not_int_amount == str(excinfo.value)


def test_add_payment_schema_amount_too_large(get_dict_for_new_payment):
    amount_too_large = 999999999
    new_payment = copy(get_dict_for_new_payment)
    new_payment["amount_in_rub"] = amount_too_large
    with pytest.raises(ValueTooLargeError) as excinfo:
        PaymentCreate(**new_payment)
    assert str(amount_too_large) == str(excinfo.value)
