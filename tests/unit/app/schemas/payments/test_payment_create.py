from copy import copy

import pytest

from app.exceptions import (NotIntegerError, NotPositiveValueError,
                            ValueTooLargeError)
from app.schemas.payments import PaymentCreate


def test_add_payment_schema_negative_price(dict_for_new_payment):
    negative_price = -100
    new_payment = copy(dict_for_new_payment)
    new_payment["price_in_rub"] = negative_price
    with pytest.raises(NotPositiveValueError) as excinfo:
        PaymentCreate(**new_payment)
    assert str(negative_price) == str(excinfo.value)


def test_add_payment_schema_price_not_int(dict_for_new_payment):
    not_int_price = "-100 ₽"
    new_payment = copy(dict_for_new_payment)
    new_payment["price_in_rub"] = not_int_price

    with pytest.raises(NotIntegerError) as excinfo:
        PaymentCreate(**new_payment)
    assert not_int_price == str(excinfo.value)


def test_add_payment_schema_price_too_large(dict_for_new_payment):
    price_too_large = 999999999
    new_payment = copy(dict_for_new_payment)
    new_payment["price_in_rub"] = price_too_large
    with pytest.raises(ValueTooLargeError) as excinfo:
        PaymentCreate(**new_payment)
    assert str(price_too_large) == str(excinfo.value)
