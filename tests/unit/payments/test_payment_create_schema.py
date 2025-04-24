from datetime import datetime

import pytest

from app.exceptions import (
    NotIntegerError,
    NotPositiveValueError,
    ValueTooLargeError,
)
from app.schemas.payments import PaymentCreate
from app.utils.tools.helpers import (
    get_date_from_datetime,
)


def test_add_payment_schema_negative_price(category):
    negative_price = -100
    new_payment = {
        "name": "test_name",
        "price_in_rub": negative_price,
        "category": category.id,
        "date": get_date_from_datetime(datetime.now()),
    }

    with pytest.raises(NotPositiveValueError) as excinfo:
        PaymentCreate(**new_payment)
    assert str(negative_price) == str(excinfo.value)


def test_add_payment_schema_price_not_int(category):
    not_int_price = "-100 ₽"
    new_payment = {
        "name": "test_name",
        "price_in_rub": not_int_price,
        "category": category.id,
        "date": get_date_from_datetime(datetime.now()),
    }

    with pytest.raises(NotIntegerError) as excinfo:
        PaymentCreate(**new_payment)
    assert not_int_price == str(excinfo.value)


def test_add_payment_schema_price_too_large(category):
    price_too_large = 999999999
    new_payment = {
        "name": "test_name",
        "price_in_rub": price_too_large,
        "category": category.id,
        "date": get_date_from_datetime(datetime.now()),
    }

    with pytest.raises(ValueTooLargeError) as excinfo:
        PaymentCreate(**new_payment)
    assert str(price_too_large) == str(excinfo.value)
