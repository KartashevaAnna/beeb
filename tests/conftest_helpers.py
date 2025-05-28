from copy import copy

from fastapi import Response

from app.models import Payment
from app.settings import SETTINGS
from app.utils.tools.helpers import convert_to_copecks, get_number_for_db


def remove_id(to_change: dict) -> dict:
    new_dict = copy(to_change)
    new_dict.pop("id", None)
    return new_dict


def change_to_a_defined_category(payment_as_dict, category) -> dict:
    new_dict = dict(payment_as_dict)
    new_dict["category_id"] = category.id
    return new_dict


def check_created_payment(
    payment_create: dict, payment: Payment, response: Response
):
    assert response.status_code == 303
    if payment_create.get("grams"):
        assert (
            response.headers.get("location")
            == SETTINGS.urls.create_payment_food
        )
    else:
        assert (
            response.headers.get("location")
            == SETTINGS.urls.create_payment_non_food
        )
    assert payment.name == payment_create["name"]
    assert payment.amount == convert_to_copecks(payment_create["amount"])
    assert payment.category_id == payment_create["category_id"]


def check_updated_payment(
    updated_payment: Payment, payment_update: dict, response: Response
):
    payment_update = copy(payment_update)
    payment_update["name"] = payment_update["name"].lower()
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    assert updated_payment.id == payment_update["id"]
    assert updated_payment.name == payment_update["name"]
    if isinstance(payment_update["amount"], str):
        payment_update["amount"] = get_number_for_db(payment_update["amount"])
        # get_number_for_db calls convert_to_copecks inside it
    else:
        payment_update["amount"] = convert_to_copecks(payment_update["amount"])
    assert updated_payment.amount == payment_update["amount"]
    assert updated_payment.payment_category.id == payment_update["category_id"]
    assert updated_payment.user_id == payment_update["user_id"]
